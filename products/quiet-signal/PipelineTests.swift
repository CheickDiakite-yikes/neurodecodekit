import Foundation

@main struct PipelineTests {
    static func main() throws {
        var checks = 0
        func check(_ condition: Bool, _ message: String) { precondition(condition, message); checks += 1 }
        let frames = (0..<30).map { i in
            FrameMeasurement(signal: [Double(i)/100, 0.4, 0.6], nuisance: Array(repeating: Double(i)/10, count: 10), time: Double(i)/10)
        }
        let observation = try aggregateFrames(frames)
        check(observation.signal.count == 6 && observation.nuisance.count == 20, "feature dimensions")
        check(abs(observation.signal[0]-0.145) < 1e-12, "mean aggregation")
        check(observation.signal[3] > 0 && observation.nuisance[10] > 0, "motion variability retained")
        do { _ = try aggregateFrames([]); preconditionFailure("empty input accepted") } catch { checks += 1 }
        let interrupted = Array(frames.prefix(10)) + Array(frames.suffix(10))
        do { _ = try aggregateFrames(interrupted); preconditionFailure("tracking gap accepted") } catch { checks += 1 }
        let root = FileManager.default.temporaryDirectory.appendingPathComponent("quiet-journal-fixture-"+UUID().uuidString)
        defer { try? FileManager.default.removeItem(at: root) }
        let journal = try Journal(root: root)
        let first = try journal.append("capture_locked_before_label", ["prediction": 0])
        let second = try journal.append("participant_label", ["label": 1])
        check(first != second, "distinct hashes")
        let data = try Data(contentsOf: journal.directory.appendingPathComponent("events.jsonl"))
        let lines = data.split(separator: 10)
        check(lines.count == 2, "one durable record per event")
        let records = try lines.map { try JSONSerialization.jsonObject(with: Data($0)) as! [String: Any] }
        let firstBody = records[0]["body"] as! [String: Any]
        let secondBody = records[1]["body"] as! [String: Any]
        check(firstBody["kind"] as? String == "capture_locked_before_label", "prediction precedes label")
        check(secondBody["previous"] as? String == first, "hash chain")
        for record in records {
            let bodyData = try JSONSerialization.data(withJSONObject: record["body"]!, options: [.sortedKeys])
            check(digest(bodyData) == record["sha256"] as? String, "hash verification")
        }
        let attrs = try FileManager.default.attributesOfItem(atPath: journal.directory.appendingPathComponent("events.jsonl").path)
        check((attrs[.posixPermissions] as? NSNumber)?.intValue == 0o600, "private file mode")
        try journal.save("fixture.json", observation)
        check(FileManager.default.fileExists(atPath: journal.directory.appendingPathComponent("fixture.json").path), "saved summary")
        do { try journal.save("oversized.json", String(repeating: "x", count: 2*1024*1024)); preconditionFailure("disk cap bypassed") } catch { checks += 1 }
        print("PASS: \(checks) generated-only pipeline checks; camera never started.")
    }
}
