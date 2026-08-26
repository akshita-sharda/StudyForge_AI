const BASE = process.env.NEXT_PUBLIC_API_URL || '/api/v1';
export const token = () => typeof window === 'undefined' ? null : localStorage.getItem('sf_token') || sessionStorage.getItem('sf_token');

export async function api(path: string, options: RequestInit = {}) {
  try {
    const res = await fetch(BASE + path, {
      ...options,
      headers: {
        ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
        ...(token() ? { Authorization: 'Bearer ' + token() } : {}),
        ...options.headers,
      },
    });
    if (!res.ok) {
      const payload = await res.json().catch(() => null);
      const detail = payload?.detail;
      const message = typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
          ? detail.map((item) => item?.msg || item?.message || String(item)).join(', ')
          : detail && typeof detail === 'object'
            ? JSON.stringify(detail)
            : `Request failed (${res.status})`;
      throw new Error(message);
    }
    return res.json();
  } catch (error) {
    if (error instanceof Error && error.message) throw error;
    throw new Error('Backend is offline. Start the StudyForge backend.');
  }
}
