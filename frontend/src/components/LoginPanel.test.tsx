import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LoginPanel } from "@/components/LoginPanel";

describe("LoginPanel", () => {
  it("shows an error for invalid credentials", async () => {
    const onSuccess = vi.fn();
    render(<LoginPanel onSuccess={onSuccess} />);

    await userEvent.type(screen.getByPlaceholderText(/user/i), "wrong");
    await userEvent.type(screen.getByPlaceholderText(/password/i), "badpass");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(screen.getByText(/invalid username or password/i)).toBeInTheDocument();
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it("calls onSuccess for valid credentials", async () => {
    const onSuccess = vi.fn();
    render(<LoginPanel onSuccess={onSuccess} />);

    await userEvent.type(screen.getByPlaceholderText(/user/i), "user");
    await userEvent.type(screen.getByPlaceholderText(/password/i), "password");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(onSuccess).toHaveBeenCalledTimes(1);
  });
});
