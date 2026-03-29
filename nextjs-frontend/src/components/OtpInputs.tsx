"use client";

import { useRef } from "react";

const DIGIT_COUNT = 6;

type OtpInputsProps = {
  onCodeChange?: (code: string) => void;
};

export default function OtpInputs({ onCodeChange }: OtpInputsProps) {
  const inputRefs = useRef<Array<HTMLInputElement | null>>([]);

  const notifyChange = () => {
    if (!onCodeChange) {
      return;
    }
    const code = inputRefs.current
      .map((input) => input?.value ?? "")
      .join("");
    onCodeChange(code);
  };

  const handleChange = (index: number) =>
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const sanitized = event.target.value.replace(/\D/g, "");
      event.target.value = sanitized;
      if (sanitized && index < DIGIT_COUNT - 1) {
        inputRefs.current[index + 1]?.focus();
      }
      notifyChange();
    };

  const handleKeyDown = (index: number) =>
    (event: React.KeyboardEvent<HTMLInputElement>) => {
      if (event.key === "Backspace" && !event.currentTarget.value && index > 0) {
        inputRefs.current[index - 1]?.focus();
      }
      if (event.key === "Backspace") {
        setTimeout(() => notifyChange(), 0);
      }
    };

  return (
    <div className="otp-grid" role="group" aria-label="One-time code">
      {Array.from({ length: DIGIT_COUNT }).map((_, index) => (
        <input
          key={`digit-${index}`}
          inputMode="numeric"
          autoComplete={index === 0 ? "one-time-code" : "off"}
          maxLength={1}
          aria-label={`Digit ${index + 1}`}
          ref={(element) => {
            inputRefs.current[index] = element;
          }}
          onChange={handleChange(index)}
          onKeyDown={handleKeyDown(index)}
        />
      ))}
    </div>
  );
}
