import { useState, useEffect } from 'react'
import { Shield, CloudRain, Wind, MapPin, CheckCircle, IndianRupee, CreditCard, Loader2 } from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
const API = API_BASE.endsWith('/api') ? API_BASE : `${API_BASE}/api`

const PLAN_PRICES = {
  basic:    29,
  standard: 49,
  pro:      79,
}

export default function PolicyPage({ user: firebaseUser, profile }) {
  const [upiId, setUpiId] = useState(profile?.upiId || '')
  const [plans, setPlans] = useState([])
  const [loadingPlans, setLoadingPlans] = useState(true)
  const [dynamicPremium, setDynamicPremium] = useState(null)
  const [payingPlan, setPayingPlan] = useState(null)

  useEffect(() => {
    setLoadingPlans(true)
    fetch(`${API}/plans`)
      .then(res => res.json())
      .then(data => {
        if (data.plans) setPlans(data.plans)
        setLoadingPlans(false)
      })
      .catch(err => { console.error(err); setLoadingPlans(false) })
  }, [])

  useEffect(() => {
    if (!profile) return
    fetch(`${API}/premium/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        plan: profile.plan || 'standard', 
        zone: 'hsr_layout', 
        platform: (profile.platform || 'swiggy').toLowerCase() 
      })
    })
      .then(res => res.json())
      .then(data => setDynamicPremium(data))
      .catch(console.error)
  }, [profile])

  const handlePayment = async (plan) => {
    if (!profile || !firebaseUser) return
    setPayingPlan(plan.id)

    try {
      const orderRes = await fetch(`${API}/payment/create-order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          planId: plan.id,
          planLabel: plan.label,
          amount: PLAN_PRICES[plan.id] || plan.weekly_premium,
          userId: firebaseUser.uid
        })
      })

      if (!orderRes.ok) throw new Error('Failed to create order')
      const orderData = await orderRes.json()

      const options = {
        key: orderData.keyId,
        amount: orderData.amount,
        currency: orderData.currency,
        name: 'ParametricGuard',
        description: `${plan.label} Plan — Weekly Premium`,
        order_id: orderData.orderId,
        prefill: {
          name: profile.name,
          email: profile.email || '',
          contact: profile.phone || '',
        },
        theme: { color: '#22c55e' },
        handler: async function (response) {
          try {
            const verifyRes = await fetch(`${API}/payment/verify`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
                planId: plan.id,
                userId: firebaseUser.uid,
                amount: PLAN_PRICES[plan.id] || plan.weekly_premium,
              })
            })

            if (verifyRes.ok) {
              alert(`Payment successful! ${plan.label} plan is now active.`)
            } else {
              alert('Verification failed.')
            }
          } catch (err) {
            alert('Error verifying payment.')
          }
          setPayingPlan(null)
        },
        modal: { ondismiss: () => setPayingPlan(null) }
      }

      const rzp = new window.Razorpay(options)
      rzp.on('payment.failed', (resp) => alert(`Failed: ${resp.error.description}`))
      rzp.open()

    } catch (err) {
      console.error(err)
      alert('Failed to initiate payment. Please try again.')
      setPayingPlan(null)
    }
  }

  if (!profile) return <div style={{ padding: '2rem', color: '#64748b' }}>Loading your profile...</div>

  const activePlan = profile.plan || 'basic'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#f1f5f9' }}>My Policy & Payout</h2>
        <p style={{ color: '#64748b', fontSize: '0.875rem', marginTop: '0.2rem' }}>Production mode: Everything synced to Firebase.</p>
      </div>

      {/* Plans Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem' }}>
        {loadingPlans ? (
          <div className="glass" style={{ padding: '2rem', textAlign: 'center', gridColumn: '1 / -1' }}>Fetching plans...</div>
        ) : plans.map(plan => {
          const price = PLAN_PRICES[plan.id] || plan.weekly_premium
          const isActive = plan.id === activePlan
          const isPaying = payingPlan === plan.id

          return (
            <div key={plan.id} className="glass stat-card" style={{ borderTop: isActive ? '3px solid #22c55e' : '3px solid #475569' }}>
               <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f1f5f9', marginBottom: '0.5rem' }}>{plan.label}</h4>
               <div style={{ marginBottom: '0.75rem' }}>
                 <span style={{ fontSize: '2rem', fontWeight: 900, color: isActive ? '#22c55e' : '#60a5fa' }}>₹{price}</span>
                 <span style={{ fontSize: '0.8rem', color: '#64748b' }}> / week</span>
               </div>
               <button
                  onClick={() => handlePayment(plan)}
                  disabled={isActive || isPaying}
                  className="btn btn-primary"
                  style={{ width: '100%', marginTop: '1rem' }}
                >
                  {isPaying ? 'Processing...' : (isActive ? 'Active Plan' : `Upgrade to ${plan.label}`)}
                </button>
            </div>
          )
        })}
      </div>
    </div>
  )
}
