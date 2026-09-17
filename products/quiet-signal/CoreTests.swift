import Foundation

@main
struct CoreTests {
    static var checks = 0
    static func check(_ condition: @autoclosure () -> Bool, _ message: String) {
        checks += 1
        if !condition() { fatalError("FAIL: \(message)") }
    }
    static func rejects(_ message: String, _ body: () throws -> Void) {
        checks += 1
        do { try body(); fatalError("FAIL: expected refusal: \(message)") }
        catch { }
    }
    static func observation(_ i: Int, label: Int, nuisanceOnly: Bool = false) -> Observation {
        let nuisance = [Double((i / 2) % 3) - 1, Double((i / 6) % 2) - 0.5]
        let value = nuisanceOnly ? nuisance[0] + 0.2 * nuisance[1] : (label == 0 ? -1.0 : 1.0)
        return Observation(signal: (0..<6).map { value * Double($0 + 1) + nuisance[0] * 0.1 },
                           nuisance: nuisance, frameCount: 60, seconds: 3)
    }
    static func training(nuisanceOnly: Bool = false) -> [LabeledTrial] {
        (0..<24).map { LabeledTrial(observation: observation($0, label: $0 % 2, nuisanceOnly: nuisanceOnly), label: $0 % 2) }
    }
    static func main() throws {
        let model = try FrozenDecoder(training: training())
        let heldout = try (24..<48).map { i -> ScoredTrial in
            let measurement = observation(i, label: i % 2)
            let prediction = try model.predict(measurement, trialIndex: i)
            check(prediction.primary == i % 2, "separable held-out fixture")
            return ScoredTrial(observation: measurement, prediction: prediction, label: i % 2)
        }
        let before = try model.predict(observation(24, label: 0), trialIndex: 24)
        _ = try score(heldout)
        _ = try model.predict(observation(25, label: 1), trialIndex: 25)
        let after = try model.predict(observation(24, label: 0), trialIndex: 24)
        let encoder = JSONEncoder()
        encoder.outputFormatting = .sortedKeys
        let beforeData = try encoder.encode(before), afterData = try encoder.encode(after)
        check(beforeData == afterData, "prediction leaves frozen state unchanged")
        let report = try score(heldout)
        check(report.primary.accuracy == 1 && report.primary.balancedAccuracy == 1, "perfect fixture metrics")
        check(abs(report.primaryFixedMarginalPermutationP - 1.0 / 2_704_156.0) < 1e-14, "known exact balanced tail")
        check(report.status == "exploratory_camera_association", "positive fixture remains only camera association")
        check(report.primaryWilson95Upper == 1 && report.primaryWilson95Lower > 0.8, "Wilson interval")
        let constantP = try fixedMarginalPermutationP(predictions: Array(repeating: 0, count: 24), labels: heldout.map { $0.label })
        check(abs(constantP - 1) < 1e-12, "constant prediction has p one")
        let reverseP = try fixedMarginalPermutationP(predictions: heldout.map { 1 - $0.label }, labels: heldout.map { $0.label })
        check(abs(reverseP - 1) < 1e-12, "inverse prediction one-sided tail")
        rejects("wrong calibration count") { _ = try FrozenDecoder(training: Array(training().prefix(23))) }
        let imbalanced = training().enumerated().map { LabeledTrial(observation: $0.element.observation, label: $0.offset < 20 ? 0 : 1) }
        rejects("calibration label imbalance") { _ = try FrozenDecoder(training: imbalanced) }
        rejects("fully nuisance explained signal") { _ = try FrozenDecoder(training: training(nuisanceOnly: true)) }
        let constant = training().map { LabeledTrial(observation: Observation(signal: Array(repeating: 0, count: 6), nuisance: $0.observation.nuisance, frameCount: 60, seconds: 3), label: $0.label) }
        rejects("zero signal") { _ = try FrozenDecoder(training: constant) }
        rejects("feature mismatch") { _ = try model.predict(Observation(signal: [0], nuisance: [0, 0], frameCount: 60, seconds: 3), trialIndex: 24) }
        rejects("nan") { _ = try model.predict(Observation(signal: [.nan, 0, 0, 0, 0, 0], nuisance: [0, 0], frameCount: 60, seconds: 3), trialIndex: 24) }
        rejects("numeric overflow") { _ = try model.predict(Observation(signal: Array(repeating: 1e308, count: 6), nuisance: [0, 0], frameCount: 60, seconds: 3), trialIndex: 24) }
        rejects("short trial") { _ = try model.predict(Observation(signal: Array(repeating: 1, count: 6), nuisance: [0, 0], frameCount: 14, seconds: 3), trialIndex: 24) }
        rejects("invalid heldout position") { _ = try model.predict(observation(0, label: 0), trialIndex: 0) }
        rejects("partial score") { _ = try score(Array(heldout.prefix(23))) }
        let imbalancedScore = heldout.enumerated().map { ScoredTrial(observation: $0.element.observation, prediction: $0.element.prediction, label: $0.offset < 20 ? 0 : 1) }
        let imbalancedReport = try score(imbalancedScore)
        check(imbalancedReport.status == "inconclusive_class_imbalance", "held-out imbalance must remain inconclusive")
        let data = try JSONEncoder().encode(report)
        let roundtrip = try JSONDecoder().decode(Evaluation.self, from: data)
        check(roundtrip.primary.correct == 24, "report roundtrip")
        print("PASS: \(checks) generated-only core checks; zero sensor, network, participant, and scientific-result operations.")
    }
}
