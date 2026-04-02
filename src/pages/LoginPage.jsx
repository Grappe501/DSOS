import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('owner@test.com')
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
    <div className="login-screen">
      <form onSubmit={onSubmit} className="login-card">
        <div className="login-brand">
          <div className="brand-logo-pill brand-logo-large">Rx</div>
          <div>
            <h1>AllCare Pharmacy</h1>
            <p>Secure staff access</p>
          </div>
        </div>

        <label className="login-label">
          Email
          <input value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>

        <label className="login-label">
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>

        <button
          type="submit"
          disabled={submitting}
          className="primary-button"
        >
          {submitting ? 'Signing in…' : 'Sign in'}
        </button>

        {error ? <div className="error-text">{error}</div> : null}
      </form>
    </div>
  )
}