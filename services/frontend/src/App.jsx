import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import './App.css' // Assuming we extract styles or keep using index.css

function App() {
    const [articles, setArticles] = useState([])
    const [query, setQuery] = useState('')
    const [searchType, setSearchType] = useState('text')
    const [selectedTopic, setSelectedTopic] = useState(null)
    const [loading, setLoading] = useState(false)

    // Realtime Status
    const [systemStatus, setSystemStatus] = useState("idle")
    const [articleCount, setArticleCount] = useState(0)
    const [newContentAvailable, setNewContentAvailable] = useState(false)
    const lastKnownCount = useRef(0)

    // Use relative URL so Vite proxy handles it
    const API_BASE = ''

    useEffect(() => {
        fetchArticles()
        // Initial status check
        checkStatus()

        // Poll for status every 10 seconds
        const interval = setInterval(checkStatus, 10000)
        return () => clearInterval(interval)
    }, [selectedTopic])

    const checkStatus = async () => {
        try {
            const res = await axios.get(`${API_BASE}/status`)
            setSystemStatus(res.data.status)
            const currentCount = res.data.article_count

            // If this is the first load, rely on the count; otherwise check for increase
            if (lastKnownCount.current > 0 && currentCount > lastKnownCount.current) {
                setNewContentAvailable(true)
            }

            if (lastKnownCount.current === 0) {
                lastKnownCount.current = currentCount
            }

            setArticleCount(currentCount)
        } catch (e) {
            console.error("Status check failed", e)
        }
    }

    const fetchArticles = async () => {
        setLoading(true)
        try {
            let url = `${API_BASE}/articles?limit=50`
            if (selectedTopic) {
                url = `${API_BASE}/topics/${selectedTopic}`
            }
            const res = await axios.get(url)
            setArticles(res.data)
            setNewContentAvailable(false)
            // Update ref to current count after fetch
            if (articles.length > 0) {
                // This logic is imperfect for "count" vs "fetched list" but good enough for MVP signal
                // Ideally we use the count from status API as the truth.
                // Let's rely on checkStatus to update the ref once we dismiss the notice.
                const statusRes = await axios.get(`${API_BASE}/status`)
                lastKnownCount.current = statusRes.data.article_count
            }
        } catch (e) {
            console.error(e)
        }
        setLoading(false)
    }

    const handleSearch = async (e) => {
        e.preventDefault()
        if (!query) return fetchArticles()

        setLoading(true)
        try {
            const res = await axios.get(`${API_BASE}/search`, {
                params: { q: query, type: searchType }
            })
            setArticles(res.data)
            setSelectedTopic(null)
        } catch (e) {
            console.error(e)
        }
        setLoading(false)
    }

    const topics = ['Politics', 'Sports', 'Business', 'Technology', 'Education', 'Crime']

    return (
        <div className="container">
            <header>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h1>BCIIP Intelligence</h1>
                    <div style={{ textAlign: 'right' }}>
                        <span className={`status-badge ${systemStatus}`}>
                            {systemStatus === 'running' ? '🟢 Crawling' : '⚪ Ideal'}
                        </span>
                        <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                            {articleCount} Articles Processed
                        </div>
                    </div>
                </div>
                <p>Real-time internet intelligence platform for Bangladesh</p>
            </header>

            {newContentAvailable && (
                <div className="notification-banner" onClick={fetchArticles}>
                    📢 New articles available! Click to refresh.
                </div>
            )}

            <form className="search-bar" onSubmit={handleSearch}>
                <input
                    type="text"
                    placeholder="Search articles..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                />
                <select value={searchType} onChange={(e) => setSearchType(e.target.value)}>
                    <option value="text">Keyword</option>
                    <option value="semantic">Semantic (AI)</option>
                </select>
                <button type="submit">Search</button>
            </form>

            <div className="filters">
                <span
                    className={`chip ${!selectedTopic ? 'active' : ''}`}
                    onClick={() => setSelectedTopic(null)}
                >
                    All
                </span>
                {topics.map(t => (
                    <span
                        key={t}
                        className={`chip ${selectedTopic === t ? 'active' : ''}`}
                        onClick={() => setSelectedTopic(t)}
                    >
                        {t}
                    </span>
                ))}
            </div>

            {loading && <p>Loading...</p>}

            <div className="article-list">
                {articles.map(article => (
                    <div key={article.id} className="article-card">
                        <h2>
                            <a href={article.url} target="_blank" rel="noopener noreferrer">
                                {article.title}
                            </a>
                        </h2>
                        <div className="meta">
                            <div>
                                <span title="When the article was published">📅 Pub: {new Date(article.published_at).toLocaleString()}</span>
                                <span style={{ marginLeft: '10px' }} title="When we acquired this data">📥 Acq: {new Date(article.created_at).toLocaleString()}</span>
                            </div>
                            <div style={{ fontSize: '0.8rem', marginTop: '4px' }}>
                                <span>{article.source}</span>
                                {article.primary_category && ` • ${article.primary_category}`}
                            </div>
                        </div>
                        {article.summary_text || (article.cleaned_text ? article.cleaned_text.substring(0, 200) + '...' : 'No content available.')}

                        {article.entities && article.entities.length > 0 && (
                            <div className="entities">
                                {article.entities.slice(0, 5).map(ent => (
                                    <span key={ent.id} className="entity-tag">{ent.text}</span>
                                ))}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    )
}

export default App
