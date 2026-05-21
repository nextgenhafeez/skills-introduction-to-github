export const content = {
  name: "Abdul Hafeez Abdul Majeed",
  title: "Software Engineer | AI Services | Product Delivery",
  summary: "Software engineer shipping production POS, AI, and consumer products across Saudi Arabia, Germany, and Canada. Full-stack delivery spanning React/TypeScript web POS, Node.js + Supabase/Firestore backends, Java monorepos, Swift/Flutter mobile apps, and AI-enabled workflows.",

  projects: [
    {
      id: "saheeh",
      title: "Saheeh POS — Restaurant Platform (Saudi Arabia)",
      description: "Multi-tenant restaurant POS for Saudi Arabia with full ZATCA Phase 2 e-invoicing, Arabic/English UI, real-time orders, kitchen + driver screens, and Stripe/Cash payments.",
      longDescription: "Saheeh is BlackLayers' multi-tenant POS platform built for the Saudi market. It covers everything a restaurant needs end-to-end: cash desk, delivery service with live driver tracking, kitchen monitor, table management, daily Z-reports, and ZATCA Phase 2 compliance (ECDSA secp256k1 CSR, Fatoora portal onboarding, real-time invoice clearance). Built on React + TypeScript, Supabase (Postgres + Realtime), Vercel, and a Leaflet/OSM map stack — no Google dependency. Live at dashboard.saheehpos.com.",
      tech: ["React", "TypeScript", "Supabase", "ZATCA Phase 2", "Leaflet/OSM", "Vercel", "Vite", "Tailwind"],
      featured: true,
      logo: "saheeh-logo.svg",
      github: "https://github.com/nextgenhafeez/saheeh-pos",
    },
    {
      id: "sushiki",
      title: "SushiKi — Multi-Branch Restaurant POS (Germany)",
      description: "End-to-end POS suite for a German sushi chain — web POS, kitchen monitor, driver app, customer app, print relay, and Liefersoft-style delivery flow across Hürth + Köln branches.",
      longDescription: "SushiKi is a full production POS suite running across two German branches (Hürth and Köln). Includes a React web POS with cash desk + delivery service, a Flutter rider app, a customer ordering app, Windows-based ESC/POS print relays per branch, real-time order sync via Firebase Firestore, Google Maps integration, and per-branch routing. Drove the architecture from single-tenant to multi-branch, including branch-scoped daily closing reports and Z-report automation.",
      tech: ["React", "TypeScript", "Firebase", "Firestore", "Flutter", "Node.js", "ESC/POS", "Google Maps"],
      featured: true,
      logo: "sushiki-logo.png",
      github: "https://github.com/nextgenhafeez",
    },
    {
      id: "sakeena",
      title: "Sakeena App",
      description: "A beautifully crafted Islamic lifestyle app featuring Prayer Times, Qibla Direction, Hijri Calendar, Tasbeeh Counter, and personalized settings.",
      longDescription: "Sakeena is a comprehensive Islamic lifestyle companion built with modern mobile technologies. It features accurate Prayer Times with notifications, a GPS-powered Qibla compass, Hijri Calendar integration, a digital Tasbeeh counter, and a polished dark-themed UI — all designed for daily spiritual practice.",
      tech: ["React", "TypeScript", "Tailwind", "Vite"],
      featured: true,
      image: "sakeena-showcase.png",
      logo: "sakeena-logo.png",
      github: "https://github.com/nextgenhafeez/sakeena-web",
    },
    {
      id: "blai",
      title: "BLAI Agent — BlackLayers AI Desktop",
      description: "Desktop AI agent with auto-update releases, custom prompt engineering pipelines, and integrated workflow automation for BlackLayers internal tooling.",
      longDescription: "BLAI is BlackLayers' in-house AI agent — a desktop application with auto-update infrastructure (GitHub Releases-based), prompt engineering pipelines, and direct integrations into internal product workflows. Ships through the blai-agent-releases channel.",
      tech: ["TypeScript", "Electron", "Node.js", "GitHub Actions", "AI/LLM"],
      featured: false,
      github: "https://github.com/nextgenhafeez/blai-agent-releases",
    },
    {
      id: "evin",
      title: "Evin — iOS Dating App",
      description: "Native iOS dating app with location-based matching, real-time chat, and a tailored European launch focused on privacy compliance.",
      longDescription: "Evin is a native iOS dating application built in Swift, featuring location-based matching, real-time messaging, profile verification, and full GDPR-compliant privacy workflows. Architected the client approval plan, European location launch strategy, and translation pipeline.",
      tech: ["Swift", "iOS", "Firebase", "Real-time Chat", "GDPR"],
      featured: false,
      github: "https://github.com/nextgenhafeez",
    },
    {
      id: "credail",
      title: "Credail Monorepo",
      description: "Cross-stack engineering monorepo — Spring Boot backend, Android Java client, Swift iOS client, and shared system documentation for a credit management product.",
      longDescription: "A comprehensive monorepo architecture showcasing cross-platform engineering — from Spring Boot backend services to Android Java and Swift iOS mobile clients, plus shared design systems and unified release tooling.",
      tech: ["Java", "Swift", "Spring Boot", "Android", "Monorepo"],
      featured: false,
      github: "https://github.com/nextgenhafeez",
    },
    {
      id: "blacklayer",
      title: "BlackLayer Leads",
      description: "Leads management platform with user authentication, email verification, custom admin functionality, and GitHub Actions CI/CD.",
      longDescription: "Full-stack leads management platform featuring secure authentication flows, automated email verification, a custom admin dashboard, and CI/CD deployment via GitHub Actions.",
      tech: ["Python", "React", "Node.js", "GitHub Actions"],
      featured: false,
      github: "https://github.com/nextgenhafeez",
    },
    {
      id: "voxcpm",
      title: "VoxCPM — Tokenizer-Free TTS",
      description: "Research fork of a tokenizer-free TTS model for multilingual speech synthesis, creative voice design, and true-to-life voice cloning.",
      longDescription: "Maintains a research fork of VoxCPM — a tokenizer-free text-to-speech model supporting multilingual speech generation, expressive voice design, and high-fidelity voice cloning. Used for evaluating production-grade speech synthesis options.",
      tech: ["Python", "PyTorch", "TTS", "ML"],
      featured: false,
      github: "https://github.com/nextgenhafeez/VoxCPM",
    }
  ],

  skills: [
    "TypeScript", "React", "Node.js", "Supabase", "Firebase", "Java", "Spring Boot", "Swift", "Flutter", "Python", "GitHub Actions", "Vercel", "Three.js", "AI / LLM"
  ],

  experience: [
    {
      role: "Founder & Software Engineering Lead",
      company: "BlackLayers",
      period: "2023 — Present",
      description: "Building Saheeh (Saudi multi-tenant restaurant POS with ZATCA Phase 2) and BLAI Agent (BlackLayers' AI desktop product). Owning full delivery: architecture, frontend, Supabase backend, ZATCA cryptographic onboarding, and deployment to Vercel."
    },
    {
      role: "Lead Engineer — SushiKi POS",
      company: "SushiKi (Hürth + Köln, Germany)",
      period: "2024 — Present",
      description: "Architected and shipped a multi-branch restaurant POS suite: React web POS, Flutter rider app, Windows print relays, and Firestore-backed real-time sync. Built per-branch Z-reports, daily closing automation, and Liefersoft-style delivery service."
    },
    {
      role: "Full Stack Developer",
      company: "Credail",
      period: "2021 — 2023",
      description: "Developed and maintained credit management platforms across a Java/Swift monorepo. Integrated complex data visualizations and ensured pixel-perfect implementation of Figma designs."
    },
    {
      role: "iOS Engineer — Evin",
      company: "Evin Dating App",
      period: "2020 — 2022",
      description: "Built the native iOS dating app from scratch — Swift client, Firebase real-time backend, location-based matching, and GDPR-compliant European launch workflows."
    }
  ],

  whatIDo: {
    frontend: {
      title: "Frontend Engineering",
      description: "Crafting performant, responsive interfaces with modern frameworks. From single-page POS apps to micro-frontends, I deliver pixel-perfect experiences in production.",
      skills: ["React", "Next.js", "TypeScript", "Tailwind CSS", "Three.js", "Framer Motion", "Vite", "MUI"]
    },
    backend: {
      title: "Backend & Platform",
      description: "Designing robust APIs, multi-tenant data models, and real-time systems. From Supabase/Postgres to Firestore to Spring Boot — backends that scale and stay observable.",
      skills: ["Node.js", "Supabase", "Firebase / Firestore", "Spring Boot", "PostgreSQL", "Vercel", "GitHub Actions", "Docker"]
    }
  },

  techStack: [
    {
      title: "Languages",
      skills: ["TypeScript", "Python", "Java", "Swift", "JavaScript", "Dart"]
    },
    {
      title: "Frontend & Mobile",
      skills: ["React", "Next.js", "Tailwind CSS", "Three.js", "Framer Motion", "Flutter", "SwiftUI"]
    },
    {
      title: "Backend & Data",
      skills: ["Node.js", "Supabase", "Firestore", "Spring Boot", "PostgreSQL", "Realtime / WebSockets"]
    },
    {
      title: "Cloud & DevOps",
      skills: ["Vercel", "GitHub Actions", "AWS", "Docker", "ZATCA / Fatoora", "ESC/POS Printing"]
    }
  ],

  contact: {
    github: "https://github.com/nextgenhafeez",
    email: "hafeez1618@outlook.com",
    linkedin: "https://linkedin.com/in/nextgenhafeez"
  }
}
