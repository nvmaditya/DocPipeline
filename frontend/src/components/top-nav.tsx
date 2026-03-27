"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
    { href: "/", label: "Home" },
    { href: "/login", label: "Login" },
    { href: "/documents", label: "Documents" },
    { href: "/search", label: "Search" },
    { href: "/ask", label: "Ask Stream" },
];

export function TopNav() {
    const pathname = usePathname();

    return (
        <nav className="topNav" aria-label="Primary">
            {links.map((link) => {
                const active =
                    pathname === link.href ||
                    (link.href !== "/" && pathname.startsWith(link.href));

                return (
                    <Link
                        key={link.href}
                        href={link.href}
                        className={`topNavLink${active ? " active" : ""}`}
                        aria-current={active ? "page" : undefined}
                    >
                        {link.label}
                    </Link>
                );
            })}
        </nav>
    );
}