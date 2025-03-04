/** @odoo-module */

import {Component, onWillDestroy, onWillStart, useEffect, useRef, useState} from "@odoo/owl";
import {loadBundle} from "@web/core/assets";

export class QRScanner extends Component {
    static template = "spp_qr_scanner.QRScanner";

    static props = {
        onScanned: {type: Function},
        isActive: {type: Boolean, optional: true},
        errorMessage: {type: String, optional: true},
    };

    setup() {
        this.state = useState({
            isScanning: false,
            error: this.props.errorMessage || null,
        });
        this.videoContainer = useRef("videoContainer");

        this.videoElement = null;
        this.canvasElement = null;
        this.stream = null;

        onWillDestroy(() => this.stopScanning());

        onWillStart(async () => {
            return Promise.all([
                loadBundle({
                    jsLibs: ["/spp_qr_scanner/static/lib/jsqr-1.4.0/jsQR.js"],
                }),
            ]);
        });

        useEffect(
            () => {
                // Handle prop changes here
                this.state.error = this.props.errorMessage;
            },
            () => [this.props.errorMessage]
        );
    }

    get hasRtcSupport() {
        return Boolean(navigator.mediaDevices && navigator.mediaDevices.getUserMedia && window.MediaStream);
    }

    async startScanning() {
        if (!this.hasRtcSupport) {
            this.state.error = "Your browser does not support camera access. Please use a modern browser.";
            return;
        }
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {facingMode: "environment"},
            });
            this.videoElement = this.videoContainer.el.querySelector("video");
            this.canvasElement = this.videoContainer.el.querySelector("canvas");
            this.videoElement.srcObject = this.stream;
            this.state.isScanning = true;
            this.scanQRCode();
        } catch (error) {
            this.state.error = "Cannot access camera. Please ensure camera permissions are granted.";
            console.error("Camera access error:", error);
        }
    }

    stopScanning() {
        if (this.stream) {
            this.stream.getTracks().forEach((track) => track.stop());
            this.stream = null;
        }
        this.state.isScanning = false;
    }

    scanQRCode() {
        if (!this.state.isScanning) return;

        const context = this.canvasElement.getContext("2d");

        if (this.videoElement.readyState === this.videoElement.HAVE_ENOUGH_DATA) {
            this.canvasElement.height = this.videoElement.videoHeight;
            this.canvasElement.width = this.videoElement.videoWidth;

            context.drawImage(this.videoElement, 0, 0, this.canvasElement.width, this.canvasElement.height);

            const imageData = context.getImageData(0, 0, this.canvasElement.width, this.canvasElement.height);

            const code = jsQR(imageData.data, imageData.width, imageData.height);

            if (code) {
                this.props.onScanned(code.data);
                this.stopScanning();
                return;
            }
        }

        requestAnimationFrame(() => this.scanQRCode());
    }
}
