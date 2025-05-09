
import { createClient } from '@supabase/supabase-js';

// When using Lovable's Supabase integration, these environment variables 
// are automatically injected into the build process
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

// Create a single supabase client for interacting with your database
export const supabase = createClient(supabaseUrl, supabaseKey);

// Helper function to check if Supabase is properly configured
export const isSupabaseConfigured = () => {
  return supabaseUrl && supabaseKey && supabaseUrl !== '' && supabaseKey !== '';
};
