import React, { useState } from 'react';
import { authService } from '../services/api';

const Login = ({ onAuth }) => {
	const [mode, setMode] = useState('login'); // 'login' | 'register'
	const [form, setForm] = useState({ username: '', email: '', password: '', role: 'client' });
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState('');

	const handleChange = (e) => {
		const { name, value } = e.target;
		setForm(f => ({ ...f, [name]: value }));
	};

	const submit = async (e) => {
		e.preventDefault();
		setLoading(true); setError('');
		try {
			if (mode === 'register') {
				await authService.register({
					username: form.username,
					email: form.email,
					password: form.password,
					role: form.role,
				});
				// After registration switch to login
				setMode('login');
				setLoading(false);
				return;
			}
			const data = await authService.login({ username: form.username, password: form.password });
			localStorage.setItem('token', data.access_token);
			localStorage.setItem('user', JSON.stringify(data.user));
			onAuth(data.user);
		} catch (err) {
			setError(err?.response?.data?.detail || err.message || 'Authentication failed');
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="login-wrapper">
			<div className="login-panel">
				<h2>{mode === 'login' ? 'Welcome Back' : 'Create Account'}</h2>
				<div className="login-subtitle">ML Power Grid Dashboard</div>
				{error && <div className="auth-error">{error}</div>}
				<form onSubmit={submit} className="auth-form">
					<div className="form-row">
						<label>Username</label>
						<input name="username" value={form.username} onChange={handleChange} required autoComplete="username" />
					</div>
					{mode === 'register' && (
						<div className="form-row">
							<label>Email</label>
							<input type="email" name="email" value={form.email} onChange={handleChange} required autoComplete="email" />
						</div>
					)}
					<div className="form-row">
						<label>Password</label>
						<input type="password" name="password" value={form.password} onChange={handleChange} required autoComplete={mode==='login' ? 'current-password':'new-password'} />
					</div>
					{mode === 'register' && (
						<div className="form-row">
							<label>Role</label>
							<select name="role" value={form.role} onChange={handleChange}>
								<option value="client">Client (View Only)</option>
								<option value="admin">Admin (Full Access)</option>
							</select>
						</div>
					)}
					<button className="primary-btn full-width" disabled={loading}>
						{loading ? (mode === 'login' ? 'Signing in...' : 'Creating...') : (mode === 'login' ? 'Login' : 'Register')}
					</button>
				</form>
				<div className="auth-toggle">
					{mode === 'login' ? (
						<>Need an account? <button className="link-btn" onClick={() => { setMode('register'); setError(''); }}>Register</button></>
					) : (
						<>Have an account? <button className="link-btn" onClick={() => { setMode('login'); setError(''); }}>Login</button></>
					)}
				</div>
			</div>
		</div>
	);
};

export default Login;

