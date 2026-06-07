import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AISidebar } from "@/components/AISidebar";

const onBoardUpdate = vi.fn();
const onClose = vi.fn();

beforeEach(() => {
  vi.clearAllMocks();
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("AISidebar", () => {
  it("renders placeholder and input", () => {
    render(<AISidebar onBoardUpdate={onBoardUpdate} onClose={onClose} />);
    expect(screen.getByText(/ask me anything about your board/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/ask or instruct/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /send/i })).toBeInTheDocument();
  });

  it("calls onClose when close button is clicked", async () => {
    render(<AISidebar onBoardUpdate={onBoardUpdate} onClose={onClose} />);
    await userEvent.click(screen.getByRole("button", { name: /close ai sidebar/i }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("sends a message and displays the AI reply", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      json: () => Promise.resolve({ message: "You have 5 columns.", boardUpdate: null }),
      ok: true,
    } as Response);

    render(<AISidebar onBoardUpdate={onBoardUpdate} onClose={onClose} />);
    const input = screen.getByPlaceholderText(/ask or instruct/i);
    await userEvent.type(input, "How many columns?");
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    expect(screen.getByText("How many columns?")).toBeInTheDocument();
    await waitFor(() =>
      expect(screen.getByText("You have 5 columns.")).toBeInTheDocument()
    );
    expect(onBoardUpdate).not.toHaveBeenCalled();
  });

  it("calls onBoardUpdate when AI returns a boardUpdate", async () => {
    const boardUpdate = {
      columns: [{ id: "col-1", title: "Backlog", cardIds: ["card-1"] }],
      cards: { "card-1": { id: "card-1", title: "New task", details: "Details." } },
    };
    global.fetch = vi.fn().mockResolvedValue({
      json: () => Promise.resolve({ message: "Added a card.", boardUpdate }),
      ok: true,
    } as Response);

    render(<AISidebar onBoardUpdate={onBoardUpdate} onClose={onClose} />);
    await userEvent.type(screen.getByPlaceholderText(/ask or instruct/i), "Add a task");
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    await waitFor(() => expect(onBoardUpdate).toHaveBeenCalledWith(boardUpdate));
  });

  it("shows error message on fetch failure", async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error("Network error"));

    render(<AISidebar onBoardUpdate={onBoardUpdate} onClose={onClose} />);
    await userEvent.type(screen.getByPlaceholderText(/ask or instruct/i), "Hello");
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    await waitFor(() =>
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument()
    );
  });

  it("clears input and disables send button while loading", async () => {
    let resolve: (v: unknown) => void;
    global.fetch = vi.fn().mockReturnValue(new Promise((r) => { resolve = r; }));

    render(<AISidebar onBoardUpdate={onBoardUpdate} onClose={onClose} />);
    const input = screen.getByPlaceholderText(/ask or instruct/i);
    await userEvent.type(input, "Loading test");
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    expect(input).toHaveValue("");
    expect(screen.getByRole("button", { name: /send/i })).toBeDisabled();
    expect(screen.getByText(/thinking/i)).toBeInTheDocument();

    resolve!({ json: () => Promise.resolve({ message: "Done.", boardUpdate: null }), ok: true });
  });

  it("sends message on Enter key", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      json: () => Promise.resolve({ message: "Reply.", boardUpdate: null }),
      ok: true,
    } as Response);

    render(<AISidebar onBoardUpdate={onBoardUpdate} onClose={onClose} />);
    const input = screen.getByPlaceholderText(/ask or instruct/i);
    await userEvent.type(input, "Enter key test{Enter}");

    await waitFor(() =>
      expect(screen.getByText("Reply.")).toBeInTheDocument()
    );
  });
});
