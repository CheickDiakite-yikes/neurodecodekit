import Foundation

@main struct SessionSupportTests {
    static func main() throws {
        var count = 0
        func check(_ condition: Bool, _ name: String) { precondition(condition, name); count += 1 }
        var clock = ActiveSessionClock()
        check(clock.remaining(at: 100_000) == 1200, "setup cannot time out")
        check(clock.elapsed(at: 100_000) == 0, "unstarted clock has no elapsed time")
        clock.start(at: 100_000)
        check(clock.remaining(at: 100_100) == 1100, "experiment counts time after first trial")
        clock.start(at: 100_100)
        check(clock.remaining(at: 100_200) == 1000, "each trial cannot reset the clock")
        clock.pause(at: 100_200)
        check(clock.remaining(at: 200_000) == 1000, "camera-off break is excluded")
        clock.start(at: 200_000)
        check(clock.remaining(at: 200_999) == 1, "budget resumes without increasing")
        check(clock.remaining(at: 201_000) == 0, "20-minute active deadline enforced")
        check(clock.remaining(at: 201_100) == 0, "remaining never negative")
        let root = FileManager.default.temporaryDirectory.appendingPathComponent("quiet-session-test-"+UUID().uuidString)
        defer { try? FileManager.default.removeItem(at: root) }
        let journal = try Journal(root: root)
        try journal.append("session_start", ["protocol": "CAMERA-T2T-1-v0", "binary_sha256": "5db40e4855ba12525ab18d1ea13152da1a8f52fca621083d4d7b80d215659f42"])
        var training: [LabeledTrial] = []
        for i in 0..<24 {
            let observation = Observation(signal: Array(repeating: Double(i), count: 6), nuisance: Array(repeating: 0, count: 20), frameCount: 30, seconds: 2.9)
            training.append(LabeledTrial(observation: observation, label: i%2))
            try journal.append("capture_locked_before_label", LockedCapture(index: i, observation: observation, prediction: nil))
            try journal.append("participant_label", ["index": i, "label": i%2])
        }
        try journal.save("calibration.json", training)
        try journal.append("model_frozen", training)
        try journal.append("incomplete", ["training_trials": "24", "heldout_trials": "0", "reason": "The 20-minute session limit was reached. This run is incomplete."])
        let events = journal.directory.appendingPathComponent("events.jsonl")
        let original = try Data(contentsOf: events)
        let saved = try SavedCalibration.load(from: journal.directory)
        check(saved.training.count == 24, "complete calibration recovered")
        check(saved.eventsSHA256 == digest(original), "source identity bound")
        check(try Data(contentsOf: events) == original, "recovery leaves the original byte-identical")
        check(SavedCalibration.latest(in: root)?.directory.resolvingSymlinksInPath().path == journal.directory.resolvingSymlinksInPath().path, "latest eligible session selected")
        try journal.save("calibration.json", Array(training.reversed()))
        do { _ = try SavedCalibration.load(from: journal.directory); preconditionFailure("mismatched calibration accepted") } catch { count += 1 }
        try journal.save("calibration.json", training)
        try journal.append("heldout_session_start", ["test": "generated"])
        do { _ = try SavedCalibration.load(from: journal.directory); preconditionFailure("test-started source accepted") } catch { count += 1 }
        try original.write(to: events)
        var corrupted = original; corrupted[20] = corrupted[20] == 97 ? 98 : 97
        try corrupted.write(to: events)
        do { _ = try SavedCalibration.load(from: journal.directory); preconditionFailure("corrupt chain accepted") } catch { count += 1 }
        print("PASS: \(count) generated-only timing and recovery checks; no sensors or participant model fits.")
    }
}
