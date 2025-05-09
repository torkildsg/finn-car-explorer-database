
import { createClient } from '@supabase/supabase-js';

// When using Lovable's Supabase integration, these environment variables 
// are automatically injected into the build process
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

// Helper function to check if Supabase is properly configured
export const isSupabaseConfigured = () => {
  return supabaseUrl && supabaseKey && supabaseUrl !== '' && supabaseKey !== '';
};

// Create a single supabase client for interacting with your database
// Only create a real client if we have valid credentials
export const supabase = isSupabaseConfigured() 
  ? createClient(supabaseUrl, supabaseKey)
  : null;

// Function to safely use supabase client
export const getSupabase = () => {
  if (!isSupabaseConfigured()) {
    console.warn('Supabase is not configured properly. Check your environment variables.');
    return null;
  }
  return supabase;
};
