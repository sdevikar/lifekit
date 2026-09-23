export function ConversationIcon() {
  return (
    <svg
      className="h-4 w-4 text-lk-muted"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.869 9.869 0 01-4.22-.9L3 20.4V5.6a2.6 2.6 0 01 2.6-2.6h10.8A2.6 2.6 0 0119 5.6v6.4m-6.5 0a2.5 2.5 0 100-5 2.5 2.5 0 000 5z"
      />
    </svg>
  );
}

export function SendIcon() {
  return (
    <svg
      className="h-4 w-4"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M12 19l9-7-9-7-9 7 9 7z"
      />
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M12 12l9-7"
      />
    </svg>
  );
}