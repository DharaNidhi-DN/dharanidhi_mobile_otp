import SendOtpForm from "@/components/SendOtpForm";

export default function Home() {
  return (
    <main>
      <div className="auth-shell">
        <div className="brand">
          <div className="brand-mark">MO</div>
          <div>
            <h1>Verify your mobile</h1>
            <p>We will send a one-time code to keep your account secure.</p>
          </div>
        </div>

        <div className="card">
          <div className="badge">Step 1 of 2</div>
          <div>
            <h2>Enter your number</h2>
            <p>Use the mobile number linked to your account.</p>
          </div>

          <SendOtpForm />

          <div className="helper">
            <span>Message frequency may vary.</span>
            <span>Carrier rates may apply.</span>
          </div>
        </div>
      </div>
    </main>
  );
}
