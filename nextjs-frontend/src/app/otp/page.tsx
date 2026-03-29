import Link from "next/link";
import { Suspense } from "react";
import OtpVerifyForm from "@/components/OtpVerifyForm";

export default function OtpPage() {
  return (
    <main>
      <div className="auth-shell">
        <div className="brand">
          <div className="brand-mark">MO</div>
          <div>
            <h1>Enter verification code</h1>
            <p>We sent a 6-digit code to your mobile number.</p>
          </div>
        </div>

        <div className="card">
          <div className="badge">Step 2 of 2</div>
          <div>
            <h2>OTP verification</h2>
            <p>Type the code exactly as it appears in the SMS.</p>
          </div>

          <Suspense fallback={<p className="form-message">Loading verification form...</p>}>
            <OtpVerifyForm />
          </Suspense>

          <div className="helper">
            <span>Code expires in 5 minutes.</span>
            <Link className="link-button" href="/">
              Edit phone number
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
