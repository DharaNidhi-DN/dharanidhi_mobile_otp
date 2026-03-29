"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export default function SendOtpForm() {
  const router = useRouter();
  const [countryCode, setCountryCode] = useState("+91");
  const [phone, setPhone] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const handleSend = async () => {
    setError(null);
    setMessage(null);

    const trimmed = phone.replace(/\s+/g, "");
    if (!trimmed) {
      setError("Enter a valid phone number.");
      return;
    }

    const fullPhone = `${countryCode}${trimmed}`;

    try {
      setIsLoading(true);
      const response = await fetch(`${API_BASE_URL}/otp/send`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone_number: fullPhone, channel: "sms" }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.detail ?? "Unable to send OTP.");
      }

      const data = await response.json();
      setMessage(`OTP sent to ${data.to}.`);
      router.push(`/otp?phone=${encodeURIComponent(fullPhone)}`);
    } catch (err) {
      const messageText =
        err instanceof Error ? err.message : "Unable to send OTP.";
      setError(messageText);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <div className="field">
        <label htmlFor="phone">Mobile number</label>
        <div className="input-row">
          <select
            id="country"
            name="country"
            value={countryCode}
            onChange={(event) => setCountryCode(event.target.value)}
          >
            <option value="+91">IN +91</option>
            <option value="+1">US +1</option>
            <option value="+44">UK +44</option>
            <option value="+61">AU +61</option>
          </select>
          <input
            id="phone"
            name="phone"
            type="tel"
            placeholder="79972 97060"
            autoComplete="tel"
            value={phone}
            onChange={(event) => setPhone(event.target.value)}
          />
        </div>
      </div>

      <div className="action-row">
        <button
          className="primary"
          type="button"
          onClick={handleSend}
          disabled={isLoading}
        >
          {isLoading ? "Sending..." : "Send OTP"}
        </button>
        <Link className="link-button" href="/otp">
          I already have a code
        </Link>
      </div>

      {error ? <p className="form-message form-error">{error}</p> : null}
      {message ? <p className="form-message form-success">{message}</p> : null}
    </>
  );
}
