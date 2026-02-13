//
//  AVCaptureDevice+Extension.swift
//  camera_macos
//
//  Created by riccardo on 04/11/22.
//  Patched: replaced deprecated devices(for:)/devices() with AVCaptureDeviceDiscoverySession (2026).
//

import Foundation
import AVFoundation

extension AVCaptureDevice {

    @available(macOS 10.15, *)
    public class func captureDevice(deviceTypes: [AVCaptureDevice.DeviceType], mediaType: AVMediaType) -> AVCaptureDevice? {
        let devices = AVCaptureDevice.DiscoverySession(deviceTypes: deviceTypes, mediaType: mediaType, position: .unspecified).devices
        return devices.first
    }

    @available(macOS 10.15, *)
    public class func captureDevices(deviceTypes: [AVCaptureDevice.DeviceType], mediaType: AVMediaType? = nil) -> [AVCaptureDevice] {
        let devices = AVCaptureDevice.DiscoverySession(deviceTypes: deviceTypes, mediaType: mediaType, position: .unspecified).devices
        return devices
    }

    /// Uses AVCaptureDeviceDiscoverySession instead of deprecated devices(for:).
    @available(macOS 10.15, *)
    public class func captureDevice(mediaType: AVMediaType) -> AVCaptureDevice? {
        let deviceTypes: [AVCaptureDevice.DeviceType] = mediaType == .video
            ? [.builtInWideAngleCamera, .externalUnknown]
            : [.builtInMicrophone, .externalUnknown]
        return captureDevice(deviceTypes: deviceTypes, mediaType: mediaType)
    }

    /// Uses AVCaptureDeviceDiscoverySession instead of deprecated devices(for:)/devices().
    @available(macOS 10.15, *)
    public class func captureDevices(mediaType: AVMediaType? = nil) -> [AVCaptureDevice] {
        if let mediaType = mediaType {
            let deviceTypes: [AVCaptureDevice.DeviceType] = mediaType == .video
                ? [.builtInWideAngleCamera, .externalUnknown]
                : [.builtInMicrophone, .externalUnknown]
            return captureDevices(deviceTypes: deviceTypes, mediaType: mediaType)
        } else {
            let video = captureDevices(deviceTypes: [.builtInWideAngleCamera, .externalUnknown], mediaType: .video)
            let audio = captureDevices(deviceTypes: [.builtInMicrophone, .externalUnknown], mediaType: .audio)
            return video + audio
        }
    }
}
