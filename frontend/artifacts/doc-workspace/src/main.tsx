import { createRoot } from "react-dom/client";
import { setAuthTokenGetter } from "@workspace/api-client-react";
import App from "./App";
import "./index.css";

// Wire JWT token from localStorage into all API client requests
setAuthTokenGetter(() => localStorage.getItem("docmind_access_token"));

createRoot(document.getElementById("root")!).render(<App />);
