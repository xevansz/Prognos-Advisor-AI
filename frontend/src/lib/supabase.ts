import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    'Missing Supabase environment variables: VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY must be set.'
  )
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
    flowType: 'pkce',
  },
})

export type { Session, User } from '@supabase/supabase-js'

export async function getAccessToken(): Promise<string | null> {
  const {
    data: { session },
  } = await supabase.auth.getSession()
  return session?.access_token ?? null
}

export async function extractTokenClaims(
  token: string
): Promise<Record<string, unknown> | null> {
  try {
    const [, payloadB64] = token.split('.')
    if (!payloadB64) return null
    const json = atob(payloadB64.replace(/-/g, '+').replace(/_/g, '/'))
    return JSON.parse(json) as Record<string, unknown>
  } catch {
    return null
  }
}

export async function verifyAndExtractSession() {
  const {
    data: { session },
    error,
  } = await supabase.auth.getSession()

  if (error || !session) return null

  const claims = await extractTokenClaims(session.access_token)

  return {
    session,
    claims,
    algorithm: (claims?.alg as string) ?? 'HS256',
    provider: (claims?.app_metadata as Record<string, unknown>)
      ?.provider as string,
    userId: session.user.id,
    email: session.user.email ?? null,
    isOAuth:
      session.user.app_metadata?.provider === 'google' ||
      session.user.app_metadata?.provider === 'github',
  }
}
