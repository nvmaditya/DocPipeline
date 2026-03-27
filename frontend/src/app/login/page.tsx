import { AuthPanel } from "@/components/auth-panel";

export default function LoginPage() {
    return (
        <main className="grid pageLayout">
            <section className="card pageIntro">
                <h1>Authentication</h1>
                <p>
                    Register, sign in, and manage the bearer token used by
                    document, search, and ask-stream requests.
                </p>
            </section>
            <AuthPanel />
        </main>
    );
}
