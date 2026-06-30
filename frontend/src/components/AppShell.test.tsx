import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AppShell } from "@/components/AppShell";

const AUTH_STORAGE_KEY = "pm-authenticated";

describe("AppShell", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("renders the login screen when signed out", async () => {
    render(<AppShell />);

    expect(await screen.findByRole("heading", { name: "Sign in" })).toBeVisible();
    expect(screen.queryByRole("heading", { name: "Kanban Studio", level: 1 })).toBeVisible();
  });

  it("signs in with valid credentials", async () => {
    render(<AppShell />);

    await userEvent.clear(await screen.findByLabelText("Username"));
    await userEvent.type(screen.getByLabelText("Username"), "user");
    await userEvent.clear(screen.getByLabelText("Password"));
    await userEvent.type(screen.getByLabelText("Password"), "password");
    await userEvent.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findAllByTestId(/column-/i)).toHaveLength(5);
    expect(window.localStorage.getItem(AUTH_STORAGE_KEY)).toBe("true");
  });

  it("rejects invalid credentials", async () => {
    render(<AppShell />);

    await userEvent.clear(await screen.findByLabelText("Username"));
    await userEvent.type(screen.getByLabelText("Username"), "wrong");
    await userEvent.clear(screen.getByLabelText("Password"));
    await userEvent.type(screen.getByLabelText("Password"), "credentials");
    await userEvent.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByText("Use username 'user' and password 'password'.")).toBeVisible();
    expect(screen.queryAllByTestId(/column-/i)).toHaveLength(0);
  });

  it("logs out and returns to the login screen", async () => {
    render(<AppShell />);

    await userEvent.click(await screen.findByRole("button", { name: "Sign in" }));
    await userEvent.click(await screen.findByRole("button", { name: "Log out" }));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Sign in" })).toBeVisible();
    });
    expect(window.localStorage.getItem(AUTH_STORAGE_KEY)).toBeNull();
  });
});