import Foundation

struct Observation: Codable {
    let signal: [Double]
    let nuisance: [Double]
    let frameCount: Int
    let seconds: Double
}

struct LabeledTrial: Codable {
    let observation: Observation
    let label: Int // 0 = YES, 1 = NO
}

struct Prediction: Codable {
    let primary: Int
    let nuisance: Int
    let prior: Int
    let time: Int
}

struct ScoredTrial: Codable {
    let observation: Observation
    let prediction: Prediction
    let label: Int
}

enum ExperimentError: Error, LocalizedError {
    case invalid(String)
    var errorDescription: String? {
        switch self { case .invalid(let message): return message }
    }
}

private func require(_ condition: Bool, _ message: String) throws {
    if !condition { throw ExperimentError.invalid(message) }
}

private func validate(_ observation: Observation, nuisanceCount: Int) throws {
    try require(observation.signal.count == 6 && observation.nuisance.count == nuisanceCount,
                "Feature dimensions changed; this session cannot be scored.")
    try require((observation.signal + observation.nuisance).allSatisfy { $0.isFinite },
                "A measurement contains non-finite values.")
    try require(observation.frameCount >= 15 && observation.seconds.isFinite && observation.seconds >= 2,
                "Each observation needs at least 15 valid frames over two seconds.")
}

private struct Scaling {
    let mean: [Double]
    let scale: [Double]
    init(_ rows: [[Double]]) {
        let localMean = (0..<rows[0].count).map { column in rows.map { $0[column] }.reduce(0, +) / Double(rows.count) }
        mean = localMean
        scale = localMean.indices.map { column in
            let variance = rows.map { pow($0[column] - localMean[column], 2) }.reduce(0, +) / Double(rows.count)
            return sqrt(variance) > 1e-12 ? sqrt(variance) : 1
        }
    }
    func apply(_ row: [Double]) -> [Double] { row.indices.map { (row[$0] - mean[$0]) / scale[$0] } }
}

private struct Centroids {
    let scaling: Scaling
    let means: [[Double]]
    init(rows: [[Double]], labels: [Int]) {
        let localScaling = Scaling(rows)
        scaling = localScaling
        let scaled = rows.map { localScaling.apply($0) }
        means = (0...1).map { label in
            let indices = labels.indices.filter { labels[$0] == label }
            return rows[0].indices.map { column in
                indices.map { scaled[$0][column] }.reduce(0, +) / Double(indices.count)
            }
        }
    }
    func predict(_ row: [Double]) throws -> Int {
        let value = scaling.apply(row)
        let distances = means.map { mean in value.indices.map { pow(value[$0] - mean[$0], 2) }.reduce(0, +) }
        try require(value.allSatisfy { $0.isFinite } && distances.allSatisfy { $0.isFinite },
                    "Measurement exceeds the decoder's numerical range; prediction refused.")
        return distances[1] < distances[0] ? 1 : 0 // Frozen deterministic tie rule.
    }
}

private func solve(_ matrix: [[Double]], _ vector: [Double]) throws -> [Double] {
    var a = zip(matrix, vector).map { $0 + [$1] }
    let size = vector.count
    for column in 0..<size {
        let pivot = (column..<size).max { abs(a[$0][column]) < abs(a[$1][column]) }!
        try require(abs(a[pivot][column]) > 1e-14, "Calibration matrix is singular.")
        a.swapAt(column, pivot)
        let divisor = a[column][column]
        for j in column...size { a[column][j] /= divisor }
        for row in 0..<size where row != column {
            let factor = a[row][column]
            for j in column...size { a[row][j] -= factor * a[column][j] }
        }
    }
    let result = a.map { $0[size] }
    try require(result.allSatisfy { $0.isFinite }, "Calibration produced invalid coefficients.")
    return result
}

/// All preprocessing and coefficients are fitted on the 24 calibration trials.
/// This is a camera classifier: residualization does not establish a neural source.
final class FrozenDecoder {
    private let nuisanceCount: Int
    private let nuisanceScaling: Scaling
    private let signalScaling: Scaling
    private let regression: [[Double]]
    private let retainedColumns: [Int]
    private let primaryClassifier: Centroids
    private let nuisanceClassifier: Centroids
    private let timeClassifier: Centroids
    private let majority: Int

    init(training: [LabeledTrial]) throws {
        try require(training.count == 24, "Exactly 24 calibration observations are required.")
        try require(training.allSatisfy { $0.label == 0 || $0.label == 1 }, "Labels must be YES or NO.")
        let labels = training.map { $0.label }
        let ones = labels.filter { $0 == 1 }.count
        try require(ones >= 8 && ones <= 16, "Calibration needs at least eight examples of each word.")
        nuisanceCount = training[0].observation.nuisance.count
        try require(nuisanceCount > 0 && nuisanceCount <= 32, "Expected one to 32 nuisance features.")
        for trial in training { try validate(trial.observation, nuisanceCount: nuisanceCount) }

        let signalRows = training.map { $0.observation.signal }
        let nuisanceRows = training.map { $0.observation.nuisance }
        let localSignalScaling = Scaling(signalRows)
        let localNuisanceScaling = Scaling(nuisanceRows)
        signalScaling = localSignalScaling
        nuisanceScaling = localNuisanceScaling
        let x = nuisanceRows.map { [1.0] + localNuisanceScaling.apply($0) }
        let y = signalRows.map { localSignalScaling.apply($0) }
        let dimension = x[0].count
        // Fixed ridge penalty; the intercept is not penalized. Never tuned on held-out labels.
        let gram = (0..<dimension).map { i in
            (0..<dimension).map { j in
                x.map { $0[i] * $0[j] }.reduce(0, +) + ((i == j && i > 0) ? 1e-6 : 0)
            }
        }
        let coefficients = try (0..<6).map { column in
            let rhs = (0..<dimension).map { i in x.indices.map { x[$0][i] * y[$0][column] }.reduce(0, +) }
            return try solve(gram, rhs)
        }
        regression = coefficients
        let residuals = x.indices.map { row in
            (0..<6).map { column in
                y[row][column] - x[row].indices.map { x[row][$0] * coefficients[column][$0] }.reduce(0, +)
            }
        }
        // Do not amplify tiny ridge leftovers into an apparent signal. Threshold is in
        // calibration-standardized input units, before residual standardization.
        let kept = (0..<6).filter { column in
            let values = residuals.map { $0[column] }
            let mean = values.reduce(0, +) / Double(values.count)
            return sqrt(values.map { pow($0 - mean, 2) }.reduce(0, +) / Double(values.count)) > 1e-4
        }
        try require(!kept.isEmpty, "No measurable camera variation remains after nuisance removal. Calibration is inconclusive.")
        retainedColumns = kept
        let residualRows = residuals.map { row in kept.map { row[$0] } }
        let primary = Centroids(rows: residualRows, labels: labels)
        let separation = primary.means[0].indices.map { pow(primary.means[0][$0] - primary.means[1][$0], 2) }.reduce(0, +)
        try require(separation > 1e-10, "Calibration has no class separation; the decoder abstains.")
        primaryClassifier = primary
        nuisanceClassifier = Centroids(rows: nuisanceRows, labels: labels)
        timeClassifier = Centroids(rows: training.indices.map { [Double($0)] }, labels: labels)
        majority = ones > 12 ? 1 : 0
    }

    /// Use the absolute trial position: held-out trials are indexed 24 through 47.
    /// Prediction reads no target, changes no parameter, and emits no confidence claim.
    func predict(_ observation: Observation, trialIndex: Int) throws -> Prediction {
        try validate(observation, nuisanceCount: nuisanceCount)
        try require((24..<48).contains(trialIndex), "Held-out trial positions must be 24 through 47.")
        let x = [1.0] + nuisanceScaling.apply(observation.nuisance)
        let y = signalScaling.apply(observation.signal)
        let residual = retainedColumns.map { column in
            y[column] - x.indices.map { x[$0] * regression[column][$0] }.reduce(0, +)
        }
        try require(residual.allSatisfy { $0.isFinite }, "Invalid residual measurement; prediction refused.")
        return try Prediction(primary: primaryClassifier.predict(residual),
                              nuisance: nuisanceClassifier.predict(observation.nuisance),
                              prior: majority, time: timeClassifier.predict([Double(trialIndex)]))
    }
}

struct ArmMetrics: Codable {
    let correct: Int
    let total: Int
    let accuracy: Double
    let balancedAccuracy: Double?
    let predictedYes: Int
    let predictedNo: Int
}

struct Evaluation: Codable {
    let primary: ArmMetrics
    let nuisance: ArmMetrics
    let prior: ArmMetrics
    let time: ArmMetrics
    let yesCount: Int
    let noCount: Int
    let heldOutMajorityAccuracy: Double
    let primaryFixedMarginalPermutationP: Double
    let primaryWilson95Lower: Double
    let primaryWilson95Upper: Double
    let status: String
    let interpretation: String
    let uncertaintyNote: String
}

private func choose(_ n: Int, _ k: Int) -> Double {
    guard k >= 0 && k <= n else { return 0 }
    let count = min(k, n - k)
    guard count > 0 else { return 1 }
    return (1...count).reduce(1.0) { $0 * Double(n - count + $1) / Double($1) }
}

/// Exact one-sided permutation tail, conditional on both fixed class margins.
/// Its validity requires exchangeable held-out labels; it does not remove temporal confounding.
func fixedMarginalPermutationP(predictions: [Int], labels: [Int]) throws -> Double {
    try require(!labels.isEmpty && labels.count == predictions.count && labels.count <= 100,
                "Permutation test requires one to 100 matched labels and predictions.")
    try require((labels + predictions).allSatisfy { $0 == 0 || $0 == 1 }, "Labels and predictions must be binary.")
    let n = labels.count
    let labelOnes = labels.filter { $0 == 1 }.count
    let predictedOnes = predictions.filter { $0 == 1 }.count
    let matches = labels.indices.filter { labels[$0] == 1 && predictions[$0] == 1 }.count
    let low = max(0, predictedOnes - (n - labelOnes))
    let high = min(labelOnes, predictedOnes)
    let tail = (max(low, matches)...high).map {
        choose(labelOnes, $0) * choose(n - labelOnes, predictedOnes - $0) / choose(n, predictedOnes)
    }.reduce(0, +)
    return min(1, max(0, tail))
}

func score(_ trials: [ScoredTrial]) throws -> Evaluation {
    try require(trials.count == 24, "Exactly 24 frozen held-out trials are required for the single score.")
    let labels = trials.map { $0.label }
    try require(labels.allSatisfy { $0 == 0 || $0 == 1 }, "Labels must be YES or NO.")
    let dimension = trials[0].observation.nuisance.count
    try require(dimension > 0 && dimension <= 32, "Expected one to 32 nuisance features.")
    for trial in trials {
        try validate(trial.observation, nuisanceCount: dimension)
        try require([trial.prediction.primary, trial.prediction.nuisance, trial.prediction.prior, trial.prediction.time]
            .allSatisfy { $0 == 0 || $0 == 1 }, "A frozen prediction is invalid.")
    }
    let yes = labels.filter { $0 == 0 }.count
    let no = labels.count - yes
    func metrics(_ predictions: [Int]) -> ArmMetrics {
        let correctYes = labels.indices.filter { labels[$0] == 0 && predictions[$0] == 0 }.count
        let correctNo = labels.indices.filter { labels[$0] == 1 && predictions[$0] == 1 }.count
        let balanced = yes > 0 && no > 0 ? (Double(correctYes) / Double(yes) + Double(correctNo) / Double(no)) / 2 : nil
        return ArmMetrics(correct: correctYes + correctNo, total: labels.count,
                          accuracy: Double(correctYes + correctNo) / Double(labels.count),
                          balancedAccuracy: balanced,
                          predictedYes: predictions.filter { $0 == 0 }.count,
                          predictedNo: predictions.filter { $0 == 1 }.count)
    }
    let primaryPredictions = trials.map { $0.prediction.primary }
    let primary = metrics(primaryPredictions)
    let nuisance = metrics(trials.map { $0.prediction.nuisance })
    let prior = metrics(trials.map { $0.prediction.prior })
    let time = metrics(trials.map { $0.prediction.time })
    let p = try fixedMarginalPermutationP(predictions: primaryPredictions, labels: labels)
    let n = Double(trials.count), z = 1.959963984540054
    let denominator = 1 + z * z / n
    let center = (primary.accuracy + z * z / (2 * n)) / denominator
    let half = z * sqrt(primary.accuracy * (1 - primary.accuracy) / n + z * z / (4 * n * n)) / denominator
    let enoughClasses = min(yes, no) >= 6
    let majorityAccuracy = Double(max(yes, no)) / n
    let aboveBaselines = primary.accuracy > max(nuisance.accuracy, max(prior.accuracy, max(time.accuracy, majorityAccuracy)))
    let status = !enoughClasses ? "inconclusive_class_imbalance" :
        (p < 0.05 && aboveBaselines ? "exploratory_camera_association" : "no_clear_held_out_evidence")
    return Evaluation(primary: primary, nuisance: nuisance, prior: prior, time: time,
                      yesCount: yes, noCount: no, heldOutMajorityAccuracy: majorityAccuracy,
                      primaryFixedMarginalPermutationP: p,
                      primaryWilson95Lower: max(0, center - half), primaryWilson95Upper: min(1, center + half),
                      status: status,
                      interpretation: !enoughClasses
                        ? "Fewer than six held-out examples of one word: inconclusive. Do not rebalance or rescore this session."
                        : "This evaluates a two-word camera association only. Baseline comparisons are descriptive. A positive result cannot establish EEG sensing, neural attribution, arbitrary thought reading, or generalization; facial, physiological, timing, and environmental cues may remain.",
                      uncertaintyNote: "One prespecified primary permutation test. Its exact tail assumes exchangeable labels; serial dependence or nonrandom word choice can invalidate that inference. The Wilson interval is descriptive and assumes independent trials. No model tuning after frozen held-out predictions; a fresh preregistered session is needed for replication.")
}
