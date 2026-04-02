import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('owner@local.test')
  const [password, setPassword] = useState('ChangeMe123!')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function onSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    try {
      await login(email, password)
      navigate('/', { replace: true })
    } catch (err) {
      setError(String(err.message || err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', background: '#f5f7fb' }}>
      <form onSubmit={onSubmit} style={{ width: 360, background: 'white', padding: 24, borderRadius: 16, boxShadow: '0 6px 20px rgba(16,24,40,.06)' }}>
        <h1 style={{ marginTop: 0 }}>Login</h1>
        <p style={{ color: '#667085' }}>Use the seeded owner account to enter the system.</p>

        <label style={{ display: 'grid', gap: 6, marginBottom: 12 }}>
          Email
          <input value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>

        <label style={{ display: 'grid', gap: 6, marginBottom: 12 }}>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>

        <button type="submit" disabled={submitting} style={{ width: '100%', padding: 10, borderRadius: 10, border: 0, background: '#2f6fed', color: 'white' }}>
          {submitting ? 'Signing in…' : 'Sign in'}
        </button>

        {error ? <div style={{ marginTop: 12, color: '#b42318' }}>{error}</div> : null}
      </form>
    </div>
  )
}
