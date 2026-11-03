import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL?.trim();
const supabasePublishableKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY?.trim();

const isSupabaseConfigured = Boolean(
  supabaseUrl &&
    supabasePublishableKey &&
    supabaseUrl !== "https://your-project.supabase.co"
);

if (!isSupabaseConfigured) {
  console.warn(
    "Supabase environment variables are not configured. Set VITE_SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY in a .env.local file before logging in."
  );
}

export const supabase = createClient(
  supabaseUrl || "https://your-project.supabase.co",
  supabasePublishableKey || "your-anon-key"
);