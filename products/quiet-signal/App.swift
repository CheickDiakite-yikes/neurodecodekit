import SwiftUI
import AppKit
import QuartzCore
import Darwin

enum Stage { case intro, prepare, settling, capturing, label, between, complete, stopped }

final class Experiment: ObservableObject {
    @Published var stage: Stage = .intro
    @Published var cameraStatus = "Camera off"
    @Published var cameraRunning = false
    @Published var faceReady = false
    @Published var message = ""
    @Published var evaluationText = ""
    @Published var evaluation: Evaluation?
    @Published var resultsDirectory: URL?
    @Published var testPhase = false
    @Published var completed = 0
    @Published var lastPrediction = ""
    @Published var lastDigest = ""
    @Published var remainingSeconds = 20*60
    @Published var savedCalibration: SavedCalibration?
    private let camera = Camera()
    private var timer: Timer?
    private var deadline = 0.0
    private var captureStart = 0.0
    private var startTime = 0.0
    private var sessionClock = ActiveSessionClock()
    private var latestFaceTime = 0.0
    private var captured: [FrameMeasurement] = []
    private var training: [LabeledTrial] = []
    private var testing: [ScoredTrial] = []
    private var decoder: FrozenDecoder?
    private var pending: LockedCapture?
    private var journal: Journal?
    private var isActiveCapture: Bool { stage == .settling || stage == .capturing }
    private var runRoot: URL { Bundle.main.bundleURL.deletingLastPathComponent().deletingLastPathComponent().appendingPathComponent("local-runs") }

    init() {
        savedCalibration = SavedCalibration.latest(in: runRoot)
        camera.onStatus = { [weak self] status, running in
            guard let self else { return }
            cameraStatus = status; cameraRunning = running
            if !running { faceReady = false }
        }
        camera.onFrame = { [weak self] frame in
            guard let self else { return }
            faceReady = frame != nil
            if let frame {
                latestFaceTime = frame.time
                if stage == .capturing, frame.time >= captureStart, frame.time <= deadline { captured.append(frame) }
            }
        }
        timer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in self?.tick() }
        NotificationCenter.default.addObserver(forName: NSApplication.willTerminateNotification, object: nil, queue: .main) { [weak self] _ in self?.stop() }
        NotificationCenter.default.addObserver(forName: NSApplication.didResignActiveNotification, object: nil, queue: .main) { [weak self] _ in
            guard let self, isActiveCapture else { return }
            fail("The app lost focus during capture. This session is incomplete; no accuracy result is produced.")
        }
    }

    func begin() {
        guard stage == .intro else { return }
        do {
            try openNewJournal()
            stage = .prepare; camera.start()
        } catch { fail(error.localizedDescription) }
    }

    private func openNewJournal() throws {
        let newJournal = try Journal(root: runRoot)
        journal = newJournal; resultsDirectory = newJournal.directory
        startTime = CACurrentMediaTime(); sessionClock = ActiveSessionClock(); remainingSeconds = 20*60
        let executableHash = try digest(Data(contentsOf: Bundle.main.executableURL!))
        try newJournal.append("session_start", ["protocol": "CAMERA-T2T-1-v1", "binary_sha256": executableHash,
            "calibration": "24", "heldout": "24", "settle_seconds": "3", "capture_seconds": "3",
            "time_limit": "1200 seconds after first trial, excluding camera-off inter-block break and setup",
            "words": "YES,NO", "audio": "disabled", "raw_video_retained": "0",
            "claim": "Exploratory camera association only; no EEG or established thought decoding."])
    }

    func recoverCalibration() {
        guard stage == .intro, let saved = savedCalibration else { return }
        do {
            let current = try SavedCalibration.load(from: saved.directory)
            guard current.eventsSHA256 == saved.eventsSHA256 else { throw ExperimentError.invalid("The saved record changed. Recovery refused.") }
            let frozen = try FrozenDecoder(training: current.training)
            try openNewJournal()
            try journal!.append("calibration_imported_for_new_test", ["source_session": current.directory.lastPathComponent,
                "source_events_sha256": current.eventsSHA256, "source_frozen_record_sha256": current.frozenRecordSHA256,
                "source_status": "incomplete; unchanged", "source_heldout_trials": "0"])
            training = current.training; decoder = frozen
            try journal!.save("calibration.json", training)
            lastDigest = try journal!.append("model_frozen", training)
            completed = 24; savedCalibration = nil; stage = .between
        } catch { fail(error.localizedDescription) }
    }

    func returnToStart() {
        guard stage == .stopped || stage == .complete else { return }
        camera.stop(); journal = nil
        captured = []; training = []; testing = []; decoder = nil; pending = nil
        deadline = 0; captureStart = 0; startTime = 0; latestFaceTime = 0
        sessionClock = ActiveSessionClock(); remainingSeconds = 20*60
        message = ""; evaluationText = ""; evaluation = nil; lastPrediction = ""; lastDigest = ""
        resultsDirectory = nil; testPhase = false; completed = 0; cameraRunning = false; faceReady = false
        savedCalibration = SavedCalibration.latest(in: runRoot)
        stage = .intro
    }

    func startTrial() {
        guard stage == .prepare, cameraRunning, faceReady, CACurrentMediaTime()-latestFaceTime < 1 else { return }
        captured = []; pending = nil
        sessionClock.start(at: CACurrentMediaTime())
        deadline = CACurrentMediaTime()+3; stage = .settling
    }

    func label(_ choice: Int) {
        guard stage == .label, let capture = pending else { return }
        // Remove the UI route immediately to prevent double submission.
        stage = .prepare; pending = nil
        do {
            try journal!.append("participant_label", ["index": capture.index, "label": choice])
            if testPhase {
                guard let prediction = capture.prediction else { throw CocoaError(.coderValueNotFound) }
                testing.append(ScoredTrial(observation: capture.observation, prediction: prediction, label: choice))
                completed = testing.count
                if testing.count == 24 { try finish() }
            } else {
                training.append(LabeledTrial(observation: capture.observation, label: choice))
                completed = training.count
                if training.count == 24 {
                    decoder = try FrozenDecoder(training: training)
                    try journal!.save("calibration.json", training)
                    lastDigest = try journal!.append("model_frozen", training)
                    sessionClock.pause(at: CACurrentMediaTime())
                    stage = .between; camera.stop(); faceReady = false
                }
            }
        } catch { fail(error.localizedDescription) }
    }

    func beginTest() {
        guard stage == .between else { return }
        do {
            try journal!.append("heldout_session_start", ["frozen_model_record": lastDigest])
            testPhase = true; completed = 0; stage = .prepare; camera.start()
        } catch { fail(error.localizedDescription) }
    }

    private func tick() {
        let now = CACurrentMediaTime()
        if now-latestFaceTime > 1 { faceReady = false }
        guard stage != .intro, stage != .complete, stage != .stopped else { return }
        remainingSeconds = Int(ceil(sessionClock.remaining(at: now)))
        if remainingSeconds == 0 { fail("The 20-minute experiment time limit was reached. Setup and the camera-off break were excluded. This run is incomplete."); return }
        if stage == .settling, now >= deadline {
            captured = []; captureStart = now; deadline = now+3; stage = .capturing
        } else if stage == .capturing, now >= deadline {
            do {
                let observation = try aggregateFrames(captured)
                let index = testPhase ? 24+testing.count : training.count
                let prediction = testPhase ? try decoder!.predict(observation, trialIndex: index) : nil
                let capture = LockedCapture(index: index, observation: observation, prediction: prediction)
                lastDigest = try journal!.append("capture_locked_before_label", capture)
                pending = capture; captured = []; stage = .label
            } catch { fail(error.localizedDescription) }
        }
    }

    private func finish() throws {
        let evaluation = try score(testing)
        self.evaluation = evaluation
        try journal!.append("evaluation", evaluation)
        try journal!.save("heldout.json", testing)
        try journal!.save("evaluation.json", evaluation)
        let encoder = JSONEncoder(); encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        evaluationText = String(decoding: try encoder.encode(evaluation), as: UTF8.self)
        lastPrediction = testing.map { $0.prediction.primary == 0 ? "YES" : "NO" }.joined(separator: "  ·  ")
        var usage = rusage(); getrusage(RUSAGE_SELF, &usage)
        try journal!.save("resources.json", ["runtime_seconds": CACurrentMediaTime()-startTime,
            "peak_process_rss_bytes": Double(usage.ru_maxrss), "retained_bytes_before_this_receipt": Double(journal!.bytes),
            "experiment_seconds_excluding_setup_and_break": sessionClock.elapsed(at: CACurrentMediaTime()),
            "raw_audio_bytes": 0, "raw_video_bytes": 0, "model_api_calls": 0])
        sessionClock.pause(at: CACurrentMediaTime()); stage = .complete; camera.stop()
    }

    func stop() {
        guard stage != .intro, stage != .complete, stage != .stopped else { camera.stop(); return }
        fail("Stopped by you. Partial trials remain locally for audit; no completed accuracy result exists.")
    }

    private func fail(_ reason: String) {
        if stage == .stopped { return }
        sessionClock.pause(at: CACurrentMediaTime())
        message = reason; stage = .stopped; captured = []; pending = nil
        _ = try? journal?.append("incomplete", ["reason": reason, "training_trials": String(training.count), "heldout_trials": String(testing.count)])
        camera.stop()
    }
}

struct QuietView: View {
    @StateObject private var experiment = Experiment()
    private let accent = Color(red: 0.61, green: 0.89, blue: 0.77)
    private var active: Bool { experiment.stage == .settling || experiment.stage == .capturing }
    var body: some View {
        ZStack {
            Color(red: 0.055, green: 0.078, blue: 0.10).ignoresSafeArea()
            if active {
                // Identical full-window content for both labels throughout settling and capture.
                VStack(spacing: 28) {
                    Image(systemName: "plus").font(.system(size: 38, weight: .ultraLight)).foregroundStyle(accent)
                    Text("Keep thinking your chosen word.").font(.title2)
                    Text("Stay silent. Let your face rest. Look at the cross.").foregroundStyle(.secondary)
                    Button("Stop session", action: experiment.stop).buttonStyle(.plain).foregroundStyle(.secondary).padding(.top, 70)
                }
            } else {
                VStack(alignment: .leading, spacing: 24) {
                    HStack(alignment: .top) {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("QUIET SIGNAL").font(.system(size: 13, weight: .bold, design: .monospaced)).tracking(4).foregroundStyle(accent)
                            Text("A first step toward thought-to-text.").font(.system(size: 32, weight: .medium, design: .serif))
                        }
                        Spacer()
                        Text("EXPERIMENT 01").font(.caption.monospaced()).foregroundStyle(.secondary).padding(.top, 4)
                    }
                    HStack(spacing: 16) {
                        badge(experiment.cameraRunning ? "Camera on" : "Camera off", experiment.cameraRunning)
                        badge("Microphone off", false)
                        badge("On this Mac", false)
                    }
                    Divider().opacity(0.4)
                    ScrollView { content.frame(maxWidth: .infinity, alignment: .topLeading) }
                        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
                    Spacer(minLength: 0)
                    HStack {
                        Text("Research prototype · Camera signals · No EEG measurement").font(.caption).foregroundStyle(.secondary)
                        Spacer()
                        if let path = experiment.resultsDirectory, experiment.stage == .complete || experiment.stage == .stopped {
                            Button("Local records") { NSWorkspace.shared.open(path) }.buttonStyle(.plain).font(.caption).foregroundStyle(accent)
                        }
                    }
                }.padding(38)
            }
        }.preferredColorScheme(.dark).frame(minWidth: 860, minHeight: 690)
    }

    @ViewBuilder private var content: some View {
        switch experiment.stage {
        case .intro:
            VStack(alignment: .leading, spacing: 22) {
                if experiment.savedCalibration != nil {
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Your 24 calibration trials are saved.").font(.headline).foregroundStyle(accent)
                        Text("The earlier run timed out before testing. Use the same frozen calibration for a new test block; the original record stays unchanged.").font(.callout).foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true)
                        Button("Use saved calibration", action: experiment.recoverCalibration).buttonStyle(PrimaryAction())
                    }.padding(16).background(.white.opacity(0.045), in: RoundedRectangle(cornerRadius: 12))
                }
                Text("Can the camera distinguish a silent YES from a silent NO?").font(.title2).fixedSize(horizontal: false, vertical: true)
                Text("This is an exploratory test of a possible correlate of silent thought. It has no demonstrated thought-reading accuracy. Even a positive result may come from subtle movement or other cues.")
                    .foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true)
                HStack(alignment: .top, spacing: 30) {
                    step("01", "Calibrate", "24 private choices. Think YES or NO without speaking or mouthing it.")
                    step("02", "Test blind", "24 new choices. Each guess is saved before you reveal the word.")
                    step("03", "Read the evidence", "All guesses appear together, with chance and nuisance comparisons.")
                }.padding(.vertical, 12)
                Text("About 10–15 minutes · Single participant · No downloads or account\nKeep lighting steady and use your built-in camera. Remove AirPods for this camera-only baseline; earbud EEG is a separate hardware research path.")
                    .font(.callout).foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true)
                Text("Only numerical camera features, your YES/NO answers, and predictions are saved in the app’s local-runs folder. No audio or video recording is saved. Clicking below starts the camera permission request.")
                    .font(.caption).foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true)
                Button("Start camera experiment", action: experiment.begin).buttonStyle(PrimaryAction())
            }
        case .prepare:
            VStack(alignment: .leading, spacing: 22) {
                phaseHeader
                Text("Choose privately. Then think it.").font(.title)
                Text("Silently choose YES or NO before starting. Use both words, vary your choices, and avoid a fixed pattern. Keep that choice through the next six seconds; do not speak or deliberately move your lips, eyes, or head.")
                    .foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true)
                Text(experiment.faceReady ? "One face detected. Ready when you are." : "Sit facing the camera in even light; keep your forehead visible.").foregroundStyle(accent)
                Text(experiment.cameraStatus).font(.caption).foregroundStyle(.secondary)
                HStack {
                    Button("I’ve chosen — begin", action: experiment.startTrial).buttonStyle(PrimaryAction())
                        .disabled(!experiment.cameraRunning || !experiment.faceReady)
                    Button("Stop session", action: experiment.stop).buttonStyle(.bordered)
                }
                Text("The screen never tells you which word to choose. Predictions stay hidden until all test trials are complete.").font(.caption).foregroundStyle(.secondary)
            }
        case .label:
            VStack(alignment: .leading, spacing: 24) {
                phaseHeader
                Image(systemName: "lock.fill").font(.largeTitle).foregroundStyle(accent)
                Text(experiment.testPhase ? "The prediction is locked." : "The camera features are locked.").font(.title)
                Text("Which word were you thinking? Report the original choice; the app has not shown its guess.").foregroundStyle(.secondary)
                HStack(spacing: 20) {
                    Button("YES") { experiment.label(0) }.buttonStyle(.bordered).controlSize(.large)
                    Button("NO") { experiment.label(1) }.buttonStyle(.bordered).controlSize(.large)
                    Spacer()
                    Button("I lost track — stop", action: experiment.stop).buttonStyle(.plain).foregroundStyle(.secondary)
                }
                Text("Saved record: \(experiment.lastDigest.prefix(20))…").font(.caption.monospaced()).foregroundStyle(.secondary)
            }
        case .between:
            VStack(alignment: .leading, spacing: 22) {
                Text("Calibration complete. Model frozen.").font(.title)
                Text("The camera is off and the experiment timer is paused. Take a break, then start a fresh capture session. Keep lighting and seating similar. Your next 24 choices are evaluation only; they cannot retrain the model.").foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true)
                Text("All test predictions remain hidden until the final report.").foregroundStyle(accent)
                Button("Begin blinded test", action: experiment.beginTest).buttonStyle(PrimaryAction())
                Button("Stop session", action: experiment.stop).buttonStyle(.plain)
            }
        case .complete:
            VStack(alignment: .leading, spacing: 12) {
                Text("Your first measured result.").font(.title)
                if let result = experiment.evaluation {
                    HStack(alignment: .top, spacing: 28) {
                        step(String(format: "%.0f%%", result.primary.accuracy*100), "Camera prediction", "\(result.primary.correct) / 24 correct")
                        step(String(format: "%.0f%%", result.nuisance.accuracy*100), "Motion + lighting", "Descriptive control")
                        step(String(format: "%.0f%%", result.prior.accuracy*100), "No-camera prior", "Training-majority baseline")
                    }
                    Text(result.interpretation).font(.callout).foregroundStyle(accent)
                }
                Text("These are the model’s held-out word predictions, in trial order. They are experimental guesses, not a transcript of your thoughts.").foregroundStyle(.secondary)
                Text(experiment.lastPrediction).font(.system(.body, design: .monospaced)).foregroundStyle(accent).textSelection(.enabled)
                ScrollView { Text(experiment.evaluationText).font(.system(size: 12, design: .monospaced)).textSelection(.enabled).frame(maxWidth: .infinity, alignment: .leading) }.frame(height: 240)
                Text("Any association needs independent replication. Self-chosen labels and serially related trials limit chance-test interpretation. No result here establishes neural attribution or free-form thought-to-text.").font(.caption).foregroundStyle(.secondary)
            }
        case .stopped:
            VStack(alignment: .leading, spacing: 20) {
                Text("Session incomplete.").font(.title)
                Text(experiment.message).foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true)
                Text("The camera is off. The app preserves partial records and does not fill in missing predictions. Review the recorded blocker before starting another run.").foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true)
                Text("Calibration completed: \(experiment.testPhase ? 24 : experiment.completed) / 24 · Test completed: \(experiment.testPhase ? experiment.completed : 0) / 24").font(.callout).foregroundStyle(accent)
                Button("Return to start", action: experiment.returnToStart).buttonStyle(PrimaryAction())
            }
        default: EmptyView()
        }
    }

    private var phaseHeader: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("\(experiment.testPhase ? "BLINDED TEST" : "CALIBRATION")  ·  \(experiment.completed+1) OF 24").font(.caption.monospaced()).foregroundStyle(accent)
            ProgressView(value: Double(experiment.completed), total: 24).tint(accent)
            Text(String(format: "Experiment time remaining: %02d:%02d · Setup and camera-off break excluded", experiment.remainingSeconds/60, experiment.remainingSeconds%60)).font(.caption).foregroundStyle(.secondary)
        }
    }
    private func badge(_ text: String, _ on: Bool) -> some View {
        HStack(spacing: 7) { Circle().fill(on ? accent : .gray).frame(width: 6, height: 6); Text(text).font(.caption) }
            .padding(.horizontal, 12).padding(.vertical, 7).background(.white.opacity(0.045), in: Capsule())
    }
    private func step(_ number: String, _ title: String, _ detail: String) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(number).font(.system(.title2, design: .monospaced)).foregroundStyle(accent)
            Text(title).font(.headline)
            Text(detail).font(.callout).foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true)
        }.frame(maxWidth: .infinity, alignment: .topLeading)
    }
}

struct PrimaryAction: ButtonStyle {
    @Environment(\.isEnabled) private var enabled
    func makeBody(configuration: Configuration) -> some View {
        configuration.label.font(.system(size: 15, weight: .semibold))
            .foregroundStyle(Color(red: 0.04, green: 0.10, blue: 0.08))
            .padding(.horizontal, 20).padding(.vertical, 13)
            .background(Color(red: 0.61, green: 0.89, blue: 0.77).opacity(enabled ? 1 : 0.35), in: RoundedRectangle(cornerRadius: 10))
            .opacity(configuration.isPressed ? 0.8 : 1)
    }
}

@main struct QuietSignalApp: App {
    var body: some Scene {
        Window("Quiet Signal", id: "main") { QuietView() }
            .defaultSize(width: 940, height: 780)
            .windowResizability(.contentMinSize)
    }
}
