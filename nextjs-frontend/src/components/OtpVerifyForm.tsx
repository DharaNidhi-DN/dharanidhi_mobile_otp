"use client";

import { useSearchParams } from "next/navigation";
import { useState } from "react";
import OtpInputs from "@/components/OtpInputs";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export default function OtpVerifyForm() {
  const searchParams = useSearchParams();
  const phone = searchParams.get("phone") ?? "";

  const [code, setCode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const handleVerify = async () => {
    setError(null);
    setMessage(null);

    if (!phone) {
      setError("Missing phone number. Go back and resend the OTP.");
      return;
    }

    if (code.length < 4) {
      setError("Enter the full OTP code.");
      return;
    }

    try {
      setIsLoading(true);
      const response = await fetch(`${API_BASE_URL}/otp/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone_number: phone, code }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.detail ?? "OTP verification failed.");
      }

      const data = await response.json();
      if (data.valid) {
        setMessage("OTP verified successfully.");
      } else {
        setError("Incorrect OTP. Please try again.");
      }
    } catch (err) {
      const messageText =
        err instanceof Error ? err.message : "OTP verification failed.";
      setError(messageText);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    setError(null);
    setMessage(null);

    if (!phone) {
      setError("Missing phone number. Go back and resend the OTP.");
      return;
    }

    try {
      setIsLoading(true);
      const response = await fetch(`${API_BASE_URL}/otp/send`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone_number: phone, channel: "sms" }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.detail ?? "Unable to resend OTP.");
      }

      setMessage("A new OTP has been sent.");
    } catch (err) {
      const messageText =
        err instanceof Error ? err.message : "Unable to resend OTP.";
      setError(messageText);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <div className="field">
        <label htmlFor="otp">One-time code</label>
        <OtpInputs onCodeChange={setCode} />
      </div>

      <div className="action-row">
        <button
          className="primary"
          type="button"
          onClick={handleVerify}
          disabled={isLoading}
        >
          {isLoading ? "Verifying..." : "Verify OTP"}
        </button>
        <button
          className="secondary"
          type="button"
          onClick={handleResend}
          disabled={isLoading}
        >
          Resend code
        </button>
      </div>

      {error ? <p className="form-message form-error">{error}</p> : null}
      {message ? <p className="form-message form-success">{message}</p> : null}
    </>
  );
}
