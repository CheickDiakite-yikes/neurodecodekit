import AVFoundation
import Vision
import Foundation
import QuartzCore

struct FrameMeasurement {
    let signal: [Double]
    let nuisance: [Double]
    let time: Double
}

// Only video is requested. Pixels live in memory and are never written to disk.
final class Camera: NSObject, AVCaptureVideoDataOutputSampleBufferDelegate {
    private let session = AVCaptureSession()
    private let control = DispatchQueue(label: "quiet.camera.control")
    private let frames = DispatchQueue(label: "quiet.camera.frames")
    private var configured = false
    private var previousTime = 0.0
    private let lifecycle = NSLock()
    private var generation = 0
    var onFrame: ((FrameMeasurement?) -> Void)?
    var onStatus: ((String, Bool) -> Void)?

    func start() {
        lifecycle.lock(); generation += 1; let token = generation; lifecycle.unlock()
        switch AVCaptureDevice.authorizationStatus(for: .video) {
        case .authorized: configureAndStart(token)
        case .notDetermined:
            AVCaptureDevice.requestAccess(for: .video) { [weak self] granted in
                guard let self, isCurrent(token) else { return }
                if granted { configureAndStart(token) }
                else { status("Camera access was declined. Enable it in System Settings → Privacy & Security → Camera.", false) }
            }
        default: status("Camera permission is off. Enable Quiet Signal in System Settings → Privacy & Security → Camera.", false)
        }
    }

    func stop() {
        lifecycle.lock(); generation += 1; lifecycle.unlock()
        control.async { [weak self] in
            self?.session.stopRunning()
            self?.status("Camera off", false)
        }
    }

    private func isCurrent(_ token: Int) -> Bool {
        lifecycle.lock(); defer { lifecycle.unlock() }; return generation == token
    }

    private func status(_ message: String, _ running: Bool) {
        DispatchQueue.main.async { [weak self] in self?.onStatus?(message, running) }
    }

    private func configureAndStart(_ token: Int) {
        control.async { [weak self] in
            guard let self, isCurrent(token) else { return }
            do {
                if !configured {
                    guard let device = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .unspecified) else {
                        status("No built-in Mac camera found. External and Continuity cameras are excluded.", false); return
                    }
                    let input = try AVCaptureDeviceInput(device: device)
                    let output = AVCaptureVideoDataOutput()
                    output.videoSettings = [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA]
                    output.alwaysDiscardsLateVideoFrames = true
                    output.setSampleBufferDelegate(self, queue: frames)
                    session.beginConfiguration()
                    session.sessionPreset = .vga640x480
                    guard session.canAddInput(input), session.canAddOutput(output) else {
                        session.commitConfiguration(); status("Camera format unavailable.", false); return
                    }
                    session.addInput(input); session.addOutput(output)
                    session.commitConfiguration()
                    configured = true
                }
                guard isCurrent(token) else { return }
                session.startRunning()
                guard isCurrent(token) else { session.stopRunning(); return }
                status(session.isRunning ? "Camera ready · video only" : "Camera did not start", session.isRunning)
            } catch { status("Camera error: \(error.localizedDescription)", false) }
        }
    }

    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        let now = CACurrentMediaTime()
        guard now - previousTime >= 0.09 else { return }
        previousTime = now
        guard let pixel = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        let request = VNDetectFaceLandmarksRequest()
        do {
            try VNImageRequestHandler(cvPixelBuffer: pixel, orientation: .up).perform([request])
            guard let faces = request.results, faces.count == 1, let face = faces.first,
                  face.confidence >= 0.8, face.boundingBox.width > 0.12,
                  let landmarks = face.landmarks,
                  let mouth = aspect(landmarks.outerLips),
                  let left = aspect(landmarks.leftEye), let right = aspect(landmarks.rightEye) else {
                DispatchQueue.main.async { [weak self] in self?.onFrame?(nil) }; return
            }
            let b = face.boundingBox
            let forehead = CGRect(x: b.minX + 0.3*b.width, y: b.minY + 0.81*b.height,
                                  width: 0.4*b.width, height: 0.12*b.height)
            guard let rgb = meanRGB(pixel, rect: forehead),
                  let global = meanRGB(pixel, rect: CGRect(x: 0, y: 0, width: 1, height: 1)), rgb[1] > 0.02,
                  rgb.allSatisfy({ $0 > 0.01 && $0 < 0.98 }) else {
                DispatchQueue.main.async { [weak self] in self?.onFrame?(nil) }; return
            }
            let nuisance = [Double(b.midX), Double(b.midY), Double(b.width), Double(b.height),
                            face.yaw?.doubleValue ?? 0, face.roll?.doubleValue ?? 0,
                            mouth, left, right, global.reduce(0,+)/3]
            let measurement = FrameMeasurement(signal: [rgb[0]/rgb[1], rgb[2]/rgb[1], rgb[1]],
                                               nuisance: nuisance, time: now)
            DispatchQueue.main.async { [weak self] in self?.onFrame?(measurement) }
        } catch { DispatchQueue.main.async { [weak self] in self?.onFrame?(nil) } }
    }

    private func aspect(_ region: VNFaceLandmarkRegion2D?) -> Double? {
        guard let region, region.pointCount > 2 else { return nil }
        let points = region.normalizedPoints
        let xs = points.map { Double($0.x) }, ys = points.map { Double($0.y) }
        let width = xs.max()! - xs.min()!
        guard width > 0.001 else { return nil }
        return (ys.max()! - ys.min()!) / width
    }

    private func meanRGB(_ pixel: CVPixelBuffer, rect: CGRect) -> [Double]? {
        CVPixelBufferLockBaseAddress(pixel, .readOnly)
        defer { CVPixelBufferUnlockBaseAddress(pixel, .readOnly) }
        let width = CVPixelBufferGetWidth(pixel), height = CVPixelBufferGetHeight(pixel)
        let strideBytes = CVPixelBufferGetBytesPerRow(pixel)
        guard let base = CVPixelBufferGetBaseAddress(pixel) else { return nil }
        let x0 = max(0, Int(rect.minX*Double(width))), x1 = min(width, Int(rect.maxX*Double(width)))
        let y0 = max(0, Int((1-rect.maxY)*Double(height))), y1 = min(height, Int((1-rect.minY)*Double(height)))
        guard x1 > x0, y1 > y0 else { return nil }
        let bytes = base.assumingMemoryBound(to: UInt8.self)
        var sums = [0.0, 0.0, 0.0], count = 0.0
        for y in stride(from: y0, to: y1, by: 4) {
            for x in stride(from: x0, to: x1, by: 4) {
                let i = y*strideBytes + x*4
                sums[0] += Double(bytes[i+2]); sums[1] += Double(bytes[i+1]); sums[2] += Double(bytes[i]); count += 1
            }
        }
        return sums.map { $0 / (count*255) }
    }
}

func aggregateFrames(_ frames: [FrameMeasurement]) throws -> Observation {
    guard frames.count >= 15, let first = frames.first, let last = frames.last,
          last.time-first.time >= 2, last.time-first.time <= 4.2 else {
        throw NSError(domain: "QuietSignal", code: 1, userInfo: [NSLocalizedDescriptionKey: "Insufficient usable camera frames. The session is incomplete; no accuracy claim is available."])
    }
    let means = (0..<3).map { j in frames.map { $0.signal[j] }.reduce(0,+)/Double(frames.count) }
    let deviations = (0..<3).map { j in
        sqrt(frames.map { pow($0.signal[j]-means[j], 2) }.reduce(0,+)/Double(frames.count))
    }
    guard zip(frames.dropFirst(), frames).allSatisfy({ $0.time > $1.time && $0.time-$1.time <= 0.5 }) else {
        throw NSError(domain: "QuietSignal", code: 2, userInfo: [NSLocalizedDescriptionKey: "Camera tracking was interrupted during the thought window. This run is incomplete."])
    }
    let nuisanceMeans = (0..<10).map { j in frames.map { $0.nuisance[j] }.reduce(0,+)/Double(frames.count) }
    let nuisanceDeviations = (0..<10).map { j in
        sqrt(frames.map { pow($0.nuisance[j]-nuisanceMeans[j], 2) }.reduce(0,+)/Double(frames.count))
    }
    return Observation(signal: means+deviations, nuisance: nuisanceMeans+nuisanceDeviations, frameCount: frames.count, seconds: last.time-first.time)
}
