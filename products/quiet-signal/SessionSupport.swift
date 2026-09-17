import Foundation

struct ActiveSessionClock {
    let limit: Double
    private var accumulated = 0.0
    private var activeSince: Double?
    init(limit: Double = 20*60) { self.limit = limit }
    mutating func start(at now: Double) { if activeSince == nil { activeSince = now } }
    mutating func pause(at now: Double) {
        if let since = activeSince { accumulated += max(0, now-since); activeSince = nil }
    }
    func elapsed(at now: Double) -> Double { accumulated + (activeSince.map { max(0, now-$0) } ?? 0) }
    func remaining(at now: Double) -> Double {
        max(0, limit-accumulated-(activeSince.map { max(0, now-$0) } ?? 0))
    }
}

struct LockedCapture: Codable { let index: Int; let observation: Observation; let prediction: Prediction? }

// Recovery is a new held-out block, never a continuation or rewrite of the old run.
// Only a completed frozen calibration with ZERO held-out operations is eligible.
struct SavedCalibration {
    let directory: URL
    let eventsSHA256: String
    let frozenRecordSHA256: String
    let training: [LabeledTrial]

    static func load(from directory: URL) throws -> SavedCalibration {
        let url = directory.appendingPathComponent("events.jsonl")
        let attributes = try FileManager.default.attributesOfItem(atPath: url.path)
        guard let size = attributes[.size] as? NSNumber, size.intValue <= 2*1024*1024 else {
            throw ExperimentError.invalid("Saved session is too large to inspect.")
        }
        let data = try Data(contentsOf: url)
        let lines = data.split(separator: 10)
        guard lines.count == 51 else { throw ExperimentError.invalid("This session is not a complete calibration-only timeout.") }
        var previous = String(repeating: "0", count: 64)
        var bodies: [[String: Any]] = [], hashes: [String] = []
        for line in lines {
            guard let record = try JSONSerialization.jsonObject(with: Data(line)) as? [String: Any],
                  let body = record["body"] as? [String: Any], let hash = record["sha256"] as? String,
                  body["previous"] as? String == previous else { throw ExperimentError.invalid("Saved session chain is invalid.") }
            let encoded = try JSONSerialization.data(withJSONObject: body, options: [.sortedKeys])
            guard digest(encoded) == hash else { throw ExperimentError.invalid("Saved session hash changed.") }
            previous = hash; hashes.append(hash); bodies.append(body)
        }
        func payload<T: Decodable>(_ index: Int, _ kind: String, as: T.Type) throws -> T {
            guard bodies[index]["kind"] as? String == kind, let text = bodies[index]["payload"] as? String else {
                throw ExperimentError.invalid("Saved session has an unexpected operation.")
            }
            return try JSONDecoder().decode(T.self, from: Data(text.utf8))
        }
        let start = try payload(0, "session_start", as: [String: String].self)
        // Exact shipped predecessor: core + camera are unchanged by this timing/UI fix.
        guard start["protocol"] == "CAMERA-T2T-1-v0",
              start["binary_sha256"] == "5db40e4855ba12525ab18d1ea13152da1a8f52fca621083d4d7b80d215659f42" else {
            throw ExperimentError.invalid("Saved calibration came from an unsupported decoder version.")
        }
        var training: [LabeledTrial] = []
        for i in 0..<24 {
            let capture = try payload(1+i*2, "capture_locked_before_label", as: LockedCapture.self)
            let label = try payload(2+i*2, "participant_label", as: [String: Int].self)
            guard capture.index == i, capture.prediction == nil, label["index"] == i,
                  let choice = label["label"], (0...1).contains(choice) else {
                throw ExperimentError.invalid("The saved run contains held-out or inconsistent data.")
            }
            training.append(LabeledTrial(observation: capture.observation, label: choice))
        }
        let frozen = try payload(49, "model_frozen", as: [LabeledTrial].self)
        let terminal = try payload(50, "incomplete", as: [String: String].self)
        guard terminal["training_trials"] == "24", terminal["heldout_trials"] == "0",
              terminal["reason"] == "The 20-minute session limit was reached. This run is incomplete." else {
            throw ExperimentError.invalid("Only a timeout before any held-out work is eligible.")
        }
        let encoder = JSONEncoder(); encoder.outputFormatting = [.sortedKeys]
        let canonical = try encoder.encode(training)
        guard try encoder.encode(frozen) == canonical,
              (try Data(contentsOf: directory.appendingPathComponent("calibration.json"))) == canonical else {
            throw ExperimentError.invalid("The frozen calibration does not match the captured trials.")
        }
        return SavedCalibration(directory: directory, eventsSHA256: digest(data), frozenRecordSHA256: hashes[49], training: training)
    }

    static func latest(in root: URL) -> SavedCalibration? {
        guard let directories = try? FileManager.default.contentsOfDirectory(at: root, includingPropertiesForKeys: [.creationDateKey]),
              let latest = directories.filter({ (try? $0.resourceValues(forKeys: [.isDirectoryKey]).isDirectory) == true }).max(by: {
                  ((try? $0.resourceValues(forKeys: [.creationDateKey]).creationDate) ?? .distantPast) <
                  ((try? $1.resourceValues(forKeys: [.creationDateKey]).creationDate) ?? .distantPast)
              }) else { return nil }
        // Never fall back through older sessions looking for a preferred outcome.
        return try? load(from: latest)
    }
}
