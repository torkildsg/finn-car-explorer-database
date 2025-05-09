
import { createClient } from '@supabase/supabase-js';

// Environment variables should be set in your deployment environment
// For development, you can use placeholder values or environment variables
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

export const supabase = createClient(supabaseUrl, supabaseKey);
