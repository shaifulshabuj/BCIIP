import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import './App.css'

function App() {
    const [articles, setArticles] = useState([])
    const [query, setQuery] = useState('')
    const [searchType, setSearchType] = useState('text')
    const [selectedTopic, setSelectedTopic] = useState(null)
    const [loading, setLoading] = useState(false)
    const [page, setPage] = useState(0)
    const [hasMore, setHasMore] = useState(true)

    // Date filters
    const [pubDateFrom, setPubDateFrom] = useState('')
    const [pubDateTo, setPubDateTo] = useState('')
    const [acqDateFrom, setAcqDateFrom] = useState('')
    const [acqDateTo, setAcqDateTo] = useState('')

    const [systemStatus, setSystemStatus] = useState("idle")
    const [articleCount, setArticleCount] = useState(0)
    const [newContentAvailable, setNewContentAvailable] = useState(false)
    const [stats, setStats] = useState(null)
    const lastKnownCount = useRef(0)

    const API_BASE = ''

    useEffect(() => {
        fetchArticles(true)
        checkStatus()
        fetchStats()
        const interval = setInterval(checkStatus, 10000)
        return () => clearInterval(interval)
    }, [selectedTopic, pubDateFrom, pubDateTo, acqDateFrom, acqDateTo])

    // Infinite scroll
    useEffect(() => {
        const handleScroll = () => {
            if (window.innerHeight + document.documentElement.scrollTop
                >= document.documentElement.offsetHeight - 200) {
                if (!loading && hasMore) {
                    fetchArticles(false)
                }
            }
        }
        window.addEventListener('scroll', handleScroll)
        return () => window.removeEventListener('scroll', handleScroll)
    }, [loading, hasMore, page])

    const checkStatus = async () => {
        try {
            const res = await axios.get(`${API_BASE}/status`)
            setSystemStatus(res.data.status)
            const currentCount = res.data.article_count

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

    const fetchStats = async () => {
        try {
            const res = await axios.get(`${API_BASE}/stats`)
            setStats(res.data)
        } catch (e) {
            console.error("Stats fetch failed", e)
        }
    }

    const fetchArticles = async (reset = false) => {
        if (loading) return

        setLoading(true)
        try {
            const currentPage = reset ? 0 : page
            const skip = currentPage * 20

            let url = `${API_BASE}/articles?limit=20&skip=${skip}`
            const params = new URLSearchParams()

            if (pubDateFrom) params.append('pub_date_from', pubDateFrom)
            if (pubDateTo) params.append('pub_date_to', pubDateTo)
            if (acqDateFrom) params.append('acq_date_from', acqDateFrom)
            if (acqDateTo) params.append('acq_date_to', acqDateTo)

            if (selectedTopic) {
                url = `${API_BASE}/topics/${selectedTopic}?skip=${skip}&limit=20`
            } else if (params.toString()) {
                url += `&${params.toString()}`
            }

            const res = await axios.get(url)

            if (reset) {
                setArticles(res.data)
                setPage(1)
            } else {
                setArticles(prev => [...prev, ...res.data])
                setPage(currentPage + 1)
            }

            setHasMore(res.data.length === 20)
            setNewContentAvailable(false)

            if (res.data.length > 0) {
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
        if (!query) return fetchArticles(true)

        setLoading(true)
        try {
            const res = await axios.get(`${API_BASE}/search`, {
                params: { q: query, type: searchType }
            })
            setArticles(res.data)
            setSelectedTopic(null)
            setHasMore(false)
        } catch (e) {
            console.error(e)
        }
        setLoading(false)
    }

    const formatDate = (dateStr) => {
        if (!dateStr) return 'N/A'
        const date = new Date(dateStr)
        const dateOnly = date.toISOString().split('T')[0].replace(/-/g, '/')
        const time = date.toTimeString().split(' ')[0]
        return `${dateOnly} ${time}`
    }

    const topics = ['Politics', 'Sports', 'Business', 'Technology', 'Education', 'Crime']

    return (
        <div className="container">
            <header>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h1>BCIIP Intelligence</h1>
                    <div style={{ textAlign: 'right' }}>
                        <span className={`status-badge ${systemStatus}`}>
                            {systemStatus === 'running' ? '🟢 Crawling' : '⚪ Idle'}
                        </span>
                        <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                            {articleCount} Articles Total
                        </div>
                    </div>
                </div>
                <p>Real-time internet intelligence platform for Bangladesh</p>
            </header>

            {newContentAvailable && (
                <div className="notification-banner" onClick={() => fetchArticles(true)}>
                    📢 New articles available! Click to refresh.
                </div>
            )}

            {stats && (
                <div style={{
                    background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
                    color: 'white',
                    padding: '15px',
                    borderRadius: '8px',
                    marginBottom: '20px',
                    border: '1px solid #475569'
                }}>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '15px' }}>
                        <div>
                            <h4 style={{ margin: '0 0 8px 0', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#94a3b8' }}>Pipeline</h4>
                            <div style={{ fontSize: '0.85rem', lineHeight: '1.6' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>📥 Acquired</span> <span>{stats.processing_stages?.acquired || 0}</span></div>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>🧹 Cleaned</span> <span>{stats.processing_stages?.cleaned || 0}</span></div>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>🏷️ Categorized</span> <span>{stats.processing_stages?.categorized || 0}</span></div>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>📝 Summarized</span> <span>{stats.processing_stages?.summarized || 0}</span></div>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>🔮 Embedded</span> <span>{stats.processing_stages?.embedded || 0}</span></div>
                            </div>
                        </div>

                        <div>
                            <h4 style={{ margin: '0 0 8px 0', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#94a3b8' }}>Top Sources</h4>
                            <div style={{ fontSize: '0.85rem', lineHeight: '1.6' }}>
                                {stats.by_source ?
                                    Object.entries(stats.by_source).sort((a, b) => b[1] - a[1]).slice(0, 4).map(([source, count]) => (
                                        <div key={source} style={{ display: 'flex', justifyContent: 'space-between', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                            <span style={{ marginRight: '10px' }}>{source}</span>
                                            <span>{count}</span>
                                        </div>
                                    )) : <div>No data</div>
                                }
                            </div>
                        </div>

                        <div>
                            <h4 style={{ margin: '0 0 8px 0', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#94a3b8' }}>Categories</h4>
                            <div style={{ fontSize: '0.85rem', lineHeight: '1.6' }}>
                                {stats.by_category ?
                                    Object.entries(stats.by_category).sort((a, b) => b[1] - a[1]).slice(0, 4).map(([cat, count]) => (
                                        <div key={cat} style={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <span style={{ textTransform: 'capitalize' }}>{cat}</span>
                                            <span>{count}</span>
                                        </div>
                                    )) : <div>No data</div>
                                }
                            </div>
                        </div>
                    </div>
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

            <div className="date-filters" style={{ marginBottom: '20px', display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'center' }}>
                <div>
                    <label style={{ fontSize: '0.85rem', marginRight: '5px' }}>📅 Pub From:</label>
                    <input type="date" value={pubDateFrom} onChange={(e) => setPubDateFrom(e.target.value)} />
                </div>
                <div>
                    <label style={{ fontSize: '0.85rem', marginRight: '5px' }}>📅 Pub To:</label>
                    <input type="date" value={pubDateTo} onChange={(e) => setPubDateTo(e.target.value)} />
                </div>
                <div>
                    <label style={{ fontSize: '0.85rem', marginRight: '5px' }}>📥 Acq From:</label>
                    <input type="date" value={acqDateFrom} onChange={(e) => setAcqDateFrom(e.target.value)} />
                </div>
                <div>
                    <label style={{ fontSize: '0.85rem', marginRight: '5px' }}>📥 Acq To:</label>
                    <input type="date" value={acqDateTo} onChange={(e) => setAcqDateTo(e.target.value)} />
                </div>
                <button onClick={() => { setPubDateFrom(''); setPubDateTo(''); setAcqDateFrom(''); setAcqDateTo('') }} style={{ padding: '5px 15px', cursor: 'pointer' }}>Clear</button>
            </div>

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
                                <span title="When the article was published">📅 Pub: {formatDate(article.published_at)}</span>
                                <span style={{ marginLeft: '10px' }} title="When we acquired this data">📥 Acq: {formatDate(article.created_at)}</span>
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

            {loading && <p style={{ textAlign: 'center', padding: '20px' }}>Loading more articles...</p>}
            {!loading && !hasMore && articles.length > 0 && <p style={{ textAlign: 'center', padding: '20px', color: '#64748b' }}>No more articles to load</p>}
            {!loading && articles.length === 0 && <p style={{ textAlign: 'center', padding: '20px', color: '#64748b' }}>No articles found</p>}
        </div>
    )
}

export default App
