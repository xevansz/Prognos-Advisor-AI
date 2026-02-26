import { Suspense } from "react";
import { RouterProvider } from "react-router";
import { router } from "./routes";
import { AppProvider } from "./context/AppContext";

export default function App() {
  return (
    <AppProvider>
      <Suspense fallback={<div className="min-h-screen bg-background" />}>
        <RouterProvider router={router} />
      </Suspense>
    </AppProvider>
  );
}
