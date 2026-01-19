import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import {
    Search,
    Calendar,
    Database,
    BarChart3,
    Layers,
    ShieldCheck,
    RefreshCcw,
    ArrowRight, Filter, X, FileText, TextQuote, Tags
} from 'lucide-react'
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
    const [selectedArticle, setSelectedArticle] = useState(null)

    // Realtime Status
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
        <div className="container fade-in">
            <header>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                        <h1>BCIIP Intelligence</h1>
                        <p>Bangladesh Continuous Internet Intelligence Platform</p>
                    </div>
                    <div style={{ textAlign: 'right', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px' }}>
                        <span className={`status-badge ${systemStatus}`}>
                            {systemStatus === 'running' ? '🟢 Live Crawling' : '⚪ Monitoring Mode'}
                        </span>
                        <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <Database size={14} /> {articleCount.toLocaleString()} Articles
                        </div>
                    </div>
                </div>
            </header>

            {newContentAvailable && (
                <div className="notification-banner" onClick={() => fetchArticles(true)}>
                    <RefreshCcw size={16} style={{ marginRight: '8px' }} />
                    New intelligence acquired. Click to synchronize.
                </div>
            )}

            {stats && (
                <section className="stats-grid">
                    <div className="stats-card">
                        <h4><Layers size={14} style={{ marginRight: '8px' }} /> Processing Pipeline</h4>
                        <div className="pipeline-item"><span>📥 Acquired</span> <span>{stats.processing_stages?.acquired || 0}</span></div>
                        <div className="pipeline-item"><span>🧹 Cleaned</span> <span>{stats.processing_stages?.cleaned || 0}</span></div>
                        <div className="pipeline-item"><span>🏷️ Categorized</span> <span>{stats.processing_stages?.categorized || 0}</span></div>
                        <div className="pipeline-item"><span>📝 Summarized</span> <span>{stats.processing_stages?.summarized || 0}</span></div>
                        <div className="pipeline-item"><span>🔮 Embedded</span> <span>{stats.processing_stages?.embedded || 0}</span></div>
                    </div>

                    <div className="stats-card">
                        <h4><BarChart3 size={14} style={{ marginRight: '8px' }} /> Top Intelligence Sources</h4>
                        {stats.by_source ?
                            Object.entries(stats.by_source).sort((a, b) => b[1] - a[1]).slice(0, 5).map(([source, count]) => (
                                <div key={source} className="pipeline-item">
                                    <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '180px' }}>{source}</span>
                                    <span>{count}</span>
                                </div>
                            )) : <div style={{ color: 'var(--text-muted)' }}>Synchronizing...</div>
                        }
                    </div>

                    <div className="stats-card">
                        <h4><ShieldCheck size={14} style={{ marginRight: '8px' }} /> Top Categories</h4>
                        {stats.by_category ?
                            Object.entries(stats.by_category).sort((a, b) => b[1] - a[1]).slice(0, 5).map(([cat, count]) => (
                                <div key={cat} className="pipeline-item">
                                    <span style={{ textTransform: 'capitalize' }}>{cat}</span>
                                    <span>{count}</span>
                                </div>
                            )) : <div style={{ color: 'var(--text-muted)' }}>Synchronizing...</div>
                        }
                    </div>
                </section>
            )}

            <section style={{ marginBottom: '40px' }}>
                <form className="search-container" onSubmit={handleSearch}>
                    <div className="search-bar">
                        <Search size={18} style={{ marginLeft: '12px', alignSelf: 'center', color: 'var(--text-muted)' }} />
                        <input
                            type="text"
                            placeholder="Search intelligence database..."
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                        />
                        <select value={searchType} onChange={(e) => setSearchType(e.target.value)}>
                            <option value="text">Keyword</option>
                            <option value="semantic">Semantic (AI)</option>
                        </select>
                    </div>
                    <button type="submit" className="search-button">Deep Search</button>
                </form>

                <div className="date-filters">
                    <div className="date-group">
                        <label><Calendar size={12} style={{ marginRight: '4px' }} /> Pub From</label>
                        <input type="date" value={pubDateFrom} onChange={(e) => setPubDateFrom(e.target.value)} />
                    </div>
                    <div className="date-group">
                        <label><Calendar size={12} style={{ marginRight: '4px' }} /> Pub To</label>
                        <input type="date" value={pubDateTo} onChange={(e) => setPubDateTo(e.target.value)} />
                    </div>
                    <div className="date-group">
                        <label><ArrowRight size={12} style={{ marginRight: '4px' }} /> Acq From</label>
                        <input type="date" value={acqDateFrom} onChange={(e) => setAcqDateFrom(e.target.value)} />
                    </div>
                    <div className="date-group">
                        <label><ArrowRight size={12} style={{ marginRight: '4px' }} /> Acq To</label>
                        <input type="date" value={acqDateTo} onChange={(e) => setAcqDateTo(e.target.value)} />
                    </div>
                    <button
                        onClick={() => { setPubDateFrom(''); setPubDateTo(''); setAcqDateFrom(''); setAcqDateTo('') }}
                        style={{ alignSelf: 'flex-end', background: 'transparent', border: 'none', color: 'var(--danger)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8125rem' }}
                    >
                        <X size={14} /> Reset
                    </button>
                </div>

                <div className="filters">
                    <div
                        className={`chip ${!selectedTopic ? 'active' : ''}`}
                        onClick={() => setSelectedTopic(null)}
                    >
                        All Signals
                    </div>
                    {topics.map(t => (
                        <div
                            key={t}
                            className={`chip ${selectedTopic === t ? 'active' : ''}`}
                            onClick={() => setSelectedTopic(t)}
                        >
                            {t}
                        </div>
                    ))}
                </div>
            </section >

            <section className="article-list">
                {articles.map((article, idx) => (
                    <div
                        key={idx}
                        className="article-card"
                        onClick={() => setSelectedArticle(article)}
                        style={{ cursor: 'pointer' }}
                    >
                        <h2>
                            <a href={article.url} target="_blank" rel="noopener noreferrer">
                                {article.title}
                            </a>
                        </h2>
                        <div className="meta">
                            <div className="meta-row">
                                <span title="Publication Date"><Calendar size={12} style={{ verticalAlign: 'middle', marginRight: '4px' }} /> Pub: {formatDate(article.published_at)}</span>
                                <span title="Acquisition Date"><RefreshCcw size={12} style={{ verticalAlign: 'middle', marginRight: '4px' }} /> Acq: {formatDate(article.created_at)}</span>
                            </div>
                            <div className="meta-row" style={{ color: 'var(--primary)', fontWeight: '600', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                <span>{article.source}</span>
                                {article.primary_category && <span> • {article.primary_category}</span>}
                            </div>
                        </div>
                        <div className="summary">
                            {article.summary_text || (article.cleaned_text ? article.cleaned_text.substring(0, 240) + '...' : 'Intelligence signal acquisition complete. Awaiting detailed analysis.')}
                        </div>

                        {article.entities && article.entities.length > 0 && (
                            <div className="entities">
                                {article.entities.slice(0, 6).map(ent => (
                                    <span key={ent.id} className="entity-tag">{ent.text}</span>
                                ))}
                            </div>
                        )}
                    </div>
                ))}
            </section>

            {loading && <div className="loading-indicator">Deep searching database...</div>}
            {!loading && !hasMore && articles.length > 0 && <div className="loading-indicator">End of intelligence stream</div>}
            {!loading && articles.length === 0 && <div className="loading-indicator">No intelligence signals found matching the current parameters</div>}
            {/* Modal */}
            {
                selectedArticle && (
                    <div className="modal-overlay" onClick={() => setSelectedArticle(null)}>
                        <div className="modal-content" onClick={e => e.stopPropagation()}>
                            <div className="modal-header">
                                <div>
                                    <span className="source-badge">{selectedArticle.source}</span>
                                    <h2>{selectedArticle.title}</h2>
                                </div>
                                <button className="close-modal" onClick={() => setSelectedArticle(null)}>
                                    <X size={20} />
                                </button>
                            </div>

                            <div className="modal-body">
                                <div className="modal-meta">
                                    <div className="meta-item">
                                        <Calendar size={14} />
                                        <span>Pub: {new Date(selectedArticle.published_at).toLocaleString()}</span>
                                    </div>
                                    <div className="meta-item">
                                        <Database size={14} />
                                        <span>Acq: {new Date(selectedArticle.created_at).toLocaleString()}</span>
                                    </div>
                                    <div className="meta-item">
                                        <Layers size={14} />
                                        <span>{selectedArticle.category || 'Uncategorized'}</span>
                                    </div>
                                </div>

                                {selectedArticle.summary && (
                                    <div className="modal-section">
                                        <h3><TextQuote size={18} /> Summary</h3>
                                        <div className="summary-text" style={{ fontSize: '1.1rem', color: 'var(--text-dim)', lineHeight: '1.6', fontStyle: 'italic' }}>
                                            {selectedArticle.summary}
                                        </div>
                                    </div>
                                )}

                                {selectedArticle.full_text && (
                                    <div className="modal-section">
                                        <h3><FileText size={18} /> Full Article</h3>
                                        <div className="full-text">
                                            {selectedArticle.full_text}
                                        </div>
                                    </div>
                                )}

                                {selectedArticle.entities && selectedArticle.entities.length > 0 && (
                                    <div className="modal-section">
                                        <h3><Tags size={18} /> Extracted Entities</h3>
                                        <div className="topic-filters" style={{ marginTop: '12px' }}>
                                            {selectedArticle.entities.map((ent, i) => (
                                                <span key={i} className="topic-tag">
                                                    {ent.name} <small style={{ opacity: 0.6, marginLeft: 4 }}>({ent.type})</small>
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                <div style={{ marginTop: '40px', textAlign: 'center' }}>
                                    <a
                                        href={selectedArticle.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="search-button"
                                        style={{ display: 'inline-flex', textDecoration: 'none' }}
                                    >
                                        View Original Source <ArrowRight size={18} style={{ marginLeft: 8 }} />
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                )
            }
        </div>
    )
}

export default App
