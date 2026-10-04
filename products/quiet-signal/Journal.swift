import Foundation
import CryptoKit

func digest(_ data: Data) -> String { SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined() }

final class Journal {
    let directory: URL
    private let handle: FileHandle
    private var lastHash = String(repeating: "0", count: 64)
    private(set) var bytes = 0
    private let encoder: JSONEncoder = {
        let encoder = JSONEncoder(); encoder.outputFormatting = [.sortedKeys]; return encoder
    }()

    init(root: URL) throws {
        directory = root.appendingPathComponent(UUID().uuidString, isDirectory: true)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        let path = directory.appendingPathComponent("events.jsonl")
        guard FileManager.default.createFile(atPath: path.path, contents: nil, attributes: [.posixPermissions: 0o600]) else {
            throw CocoaError(.fileWriteUnknown)
        }
        handle = try FileHandle(forWritingTo: path)
    }

    // The observation and hidden prediction are synchronized before label buttons appear.
    // Hashes provide auditability, not tamper-proofing against the computer's owner.
    @discardableResult func append<T: Encodable>(_ kind: String, _ value: T) throws -> String {
        let payload = try encoder.encode(value)
        let body: [String: Any] = ["kind": kind, "utc": ISO8601DateFormatter().string(from: Date()),
                                  "previous": lastHash, "payload": String(decoding: payload, as: UTF8.self)]
        let bodyData = try JSONSerialization.data(withJSONObject: body, options: [.sortedKeys])
        let hash = digest(bodyData)
        let record: [String: Any] = ["body": body, "sha256": hash]
        var data = try JSONSerialization.data(withJSONObject: record, options: [.sortedKeys])
        data.append(10)
        guard bytes + data.count <= 2*1024*1024 else { throw CocoaError(.fileWriteOutOfSpace) }
        try handle.write(contentsOf: data); try handle.synchronize()
        bytes += data.count; lastHash = hash
        return hash
    }

    func save<T: Encodable>(_ name: String, _ value: T) throws {
        let data = try encoder.encode(value)
        guard bytes + data.count <= 2*1024*1024 else { throw CocoaError(.fileWriteOutOfSpace) }
        let url = directory.appendingPathComponent(name)
        try data.write(to: url, options: [.atomic])
        try FileManager.default.setAttributes([.posixPermissions: 0o600], ofItemAtPath: url.path)
        bytes += data.count
    }

    deinit { try? handle.close() }
}
