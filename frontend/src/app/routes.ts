import { createBrowserRouter } from "react-router";
import { Root } from "./pages/Root";
import { Landing } from "./pages/Landing";
import { Login } from "./pages/Login";
import { Signup } from "./pages/Signup";
import { Overview } from "./pages/Overview";
import { Profile } from "./pages/Profile";
import { Settings } from "./pages/Settings";
import { Accounts } from "./pages/Accounts";
import { Transactions } from "./pages/Transactions";
import { PrognosisAI } from "./pages/PrognosisAI";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Landing,
  },
  {
    path: "/login",
    Component: Login,
  },
  {
    path: "/signup",
    Component: Signup,
  },
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
]);
