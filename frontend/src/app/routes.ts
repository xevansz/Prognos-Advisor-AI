import { createBrowserRouter } from "react-router";
import { lazy } from "react";
import { Root } from "./pages/Root";

export const Landing = lazy(() =>
  import("./pages/Landing").then((m) => ({ default: m.Landing })),
);
export const Login = lazy(() =>
  import("./pages/Login").then((m) => ({ default: m.Login })),
);
export const Signup = lazy(() =>
  import("./pages/Signup").then((m) => ({ default: m.Signup })),
);
export const ForgotPassword = lazy(() =>
  import("./pages/ForgotPassword").then((m) => ({ default: m.ForgotPassword })),
);
export const Overview = lazy(() =>
  import("./pages/Overview").then((m) => ({ default: m.Overview })),
);
export const Profile = lazy(() =>
  import("./pages/Profile").then((m) => ({ default: m.Profile })),
);
export const Settings = lazy(() =>
  import("./pages/Settings").then((m) => ({ default: m.Settings })),
);
export const Accounts = lazy(() =>
  import("./pages/Accounts").then((m) => ({ default: m.Accounts })),
);
export const Transactions = lazy(() =>
  import("./pages/Transactions").then((m) => ({ default: m.Transactions })),
);
export const PrognosisAI = lazy(() =>
  import("./pages/PrognosisAI").then((m) => ({ default: m.PrognosisAI })),
);
export const NotFound = lazy(() =>
  import("./pages/NotFound").then((m) => ({ default: m.NotFound })),
);

export const router = createBrowserRouter([
  { path: "/", Component: Landing },
  { path: "/login", Component: Login },
  { path: "/signup", Component: Signup },
  { path: "/forgot-password", Component: ForgotPassword },
  {
    path: "/dashboard",
    Component: Root,
    children: [
      { index: true, Component: Overview },
      { path: "profile", Component: Profile },
      { path: "settings", Component: Settings },
      { path: "accounts", Component: Accounts },
      { path: "transactions", Component: Transactions },
      { path: "prognosis", Component: PrognosisAI },
    ],
  },
  { path: "*", Component: NotFound },
]);
