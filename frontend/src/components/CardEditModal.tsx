"use client";

import { FormEvent, useState } from "react";
import type { Card } from "@/lib/kanban";

type CardEditModalProps = {
  card: Card;
  onSave: (cardId: string, title: string, details: string) => void;
  onCancel: () => void;
};

export const CardEditModal = ({ card, onSave, onCancel }: CardEditModalProps) => {
  const [title, setTitle] = useState(card.title);
  const [details, setDetails] = useState(card.details);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSave(card.id, title, details);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur">
      <div className="w-full max-w-md rounded-[32px] border border-[var(--stroke)] bg-white p-8 shadow-[var(--shadow)]">
        <h2 className="mb-6 text-2xl font-semibold text-[var(--navy-dark)]">
          Edit card
        </h2>

        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <label className="flex flex-col gap-2 text-sm font-semibold text-[var(--navy-dark)]">
            Title
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="rounded-3xl border border-[var(--stroke)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
              required
            />
          </label>

          <label className="flex flex-col gap-2 text-sm font-semibold text-[var(--navy-dark)]">
            Details
            <textarea
              value={details}
              onChange={(e) => setDetails(e.target.value)}
              rows={4}
              className="rounded-3xl border border-[var(--stroke)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
            />
          </label>

          <div className="flex gap-3">
            <button
              type="submit"
              className="flex-1 rounded-full bg-[var(--primary-blue)] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#167fb8]"
            >
              Save
            </button>
            <button
              type="button"
              onClick={onCancel}
              className="flex-1 rounded-full border border-[var(--stroke)] bg-white px-5 py-3 text-sm font-semibold text-[var(--navy-dark)] transition hover:bg-[var(--surface)]"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
