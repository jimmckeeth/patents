import os
import json
import pandas as pd

def main():
    # Paths relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, "data")
    output_path = os.path.join(project_root, "portal.html")
    
    my_patents_file = os.path.join(data_dir, "my-patents.csv")
    citing_patents_file = os.path.join(data_dir, "citing-patents.csv")
    forward_citations_file = os.path.join(data_dir, "forward_citations.csv")
    
    # Check if files exist
    if not all(os.path.exists(f) for f in [my_patents_file, citing_patents_file, forward_citations_file]):
        print("Error: Missing required CSV files in data/ directory. Run scripts/get_citations.py first.")
        return
        
    print("Loading datasets...")
    import re
    def get_clean_patent_id(pat_id):
        if not isinstance(pat_id, str):
            return ""
        # Remove all non-alphanumeric characters, convert to uppercase
        clean = re.sub(r'[^A-Z0-9]', '', pat_id.upper())
        # Match US + 4-digit year + sequence digits + kind code
        match = re.match(r'^US(19\d{2}|20\d{2})0*(\d+)([A-Z]\d*)$', clean)
        if match:
            return 'US' + match.group(1) + match.group(2) + match.group(3)
        return clean

    print("Loading datasets...")
    df_my = pd.read_csv(my_patents_file).fillna("")
    df_citing = pd.read_csv(citing_patents_file).fillna("")
    df_fw = pd.read_csv(forward_citations_file).fillna("")
    
    # Pre-process datasets to JSON-safe structures
    # 1. My Patents
    df_my['id_normalized'] = df_my['Document ID'].apply(get_clean_patent_id)
    my_patents_list = df_my.to_dict(orient='records')
    
    # 2. Citing Patents
    citing_patents_list = df_citing.to_dict(orient='records')
    
    # 3. Forward Citations
    df_fw['cited_patent_normalized'] = df_fw['cited_patent'].apply(get_clean_patent_id)
    fw_citations_list = df_fw.to_dict(orient='records')
    
    print("Serializing data...")
    data_payload = {
        "myPatents": my_patents_list,
        "citingPatents": citing_patents_list,
        "forwardCitations": fw_citations_list
    }
    
    json_data = json.dumps(data_payload, indent=2)
    
    print("Generating portal.html...")
    
    html_content = f"""<!DOCTYPE html>
<html lang="en" class="dark-theme">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>James McKeeth Patent Citation Intelligence Portal</title>
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        :root {{
            --bg-primary: #0b0f19;
            --bg-secondary: #111827;
            --bg-card: rgba(17, 24, 39, 0.7);
            --border-color: rgba(255, 255, 255, 0.08);
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --accent-primary: #6366f1;
            --accent-secondary: #a855f7;
            --accent-gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            --accent-hover: #4f46e5;
            --success: #10b981;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --shadow-accent: 0 10px 25px -5px rgba(99, 102, 241, 0.3);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --glass-blur: blur(12px);
        }}

        .light-theme {{
            --bg-primary: #f8fafc;
            --bg-secondary: #ffffff;
            --bg-card: rgba(255, 255, 255, 0.85);
            --border-color: rgba(0, 0, 0, 0.06);
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --accent-primary: #4f46e5;
            --accent-secondary: #9333ea;
            --accent-gradient: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%);
            --accent-hover: #4338ca;
            --success: #059669;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            --shadow-lg: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.03);
            --shadow-accent: 0 10px 25px -5px rgba(79, 70, 229, 0.15);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            transition: background-color 0.25s ease, border-color 0.25s ease, color 0.15s ease;
        }}

        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
            line-height: 1.5;
        }}

        h1, h2, h3, h4, h5, h6, .brand-title {{
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
        }}

        /* Scrollbar styles */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: var(--bg-primary);
        }}
        ::-webkit-scrollbar-thumb {{
            background: var(--border-color);
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--accent-primary);
        }}

        /* App Container */
        .app-container {{
            display: flex;
            min-height: 100vh;
        }}

        /* Sidebar styling */
        .sidebar {{
            width: 260px;
            background-color: var(--bg-secondary);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            padding: 24px 16px;
            flex-shrink: 0;
            position: sticky;
            top: 0;
            height: 100vh;
        }}

        .brand-section {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 32px;
            padding: 0 8px;
        }}

        .brand-icon {{
            width: 40px;
            height: 40px;
            border-radius: var(--radius-md);
            background: var(--accent-gradient);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 20px;
            box-shadow: var(--shadow-accent);
        }}

        .brand-title {{
            font-size: 18px;
            font-weight: 700;
            letter-spacing: -0.5px;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .nav-menu {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .nav-item button {{
            width: 100%;
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            background: transparent;
            border: none;
            border-radius: var(--radius-sm);
            color: var(--text-secondary);
            font-family: 'Outfit', sans-serif;
            font-size: 15px;
            font-weight: 500;
            cursor: pointer;
            text-align: left;
        }}

        .nav-item button:hover {{
            background-color: rgba(99, 102, 241, 0.06);
            color: var(--text-primary);
        }}

        .nav-item.active button {{
            background: var(--accent-gradient);
            color: white;
            box-shadow: var(--shadow-accent);
        }}

        .nav-item.active button i {{
            color: white;
        }}

        .sidebar-footer {{
            margin-top: auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 8px 0;
            border-top: 1px solid var(--border-color);
        }}

        .theme-toggle-btn {{
            background: transparent;
            border: 1px solid var(--border-color);
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-secondary);
            cursor: pointer;
        }}

        .theme-toggle-btn:hover {{
            color: var(--text-primary);
            border-color: var(--accent-primary);
        }}

        /* Main Content */
        .main-content {{
            flex-grow: 1;
            padding: 32px 40px;
            overflow-y: auto;
            max-width: 1400px;
            margin: 0 auto;
            width: 100%;
        }}

        .header-section {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 32px;
        }}

        .header-title {{
            font-size: 28px;
            font-weight: 700;
            letter-spacing: -0.75px;
        }}

        .header-subtitle {{
            font-size: 14px;
            color: var(--text-secondary);
            margin-top: 4px;
        }}

        /* Stats Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 32px;
        }}

        .stat-card {{
            background-color: var(--bg-card);
            backdrop-filter: var(--glass-blur);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 24px;
            box-shadow: var(--shadow-sm);
            display: flex;
            align-items: center;
            gap: 20px;
        }}

        .stat-icon {{
            width: 48px;
            height: 48px;
            border-radius: var(--radius-md);
            background: rgba(99, 102, 241, 0.1);
            color: var(--accent-primary);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }}

        .stat-card:nth-child(2) .stat-icon {{
            background: rgba(168, 85, 247, 0.1);
            color: var(--accent-secondary);
        }}

        .stat-card:nth-child(3) .stat-icon {{
            background: rgba(16, 185, 129, 0.1);
            color: var(--success);
        }}

        .stat-info {{
            display: flex;
            flex-direction: column;
        }}

        .stat-value {{
            font-size: 26px;
            font-weight: 700;
            font-family: 'Outfit', sans-serif;
            line-height: 1.2;
        }}

        .stat-label {{
            font-size: 13px;
            color: var(--text-secondary);
            font-weight: 500;
            margin-top: 2px;
        }}

        /* Filter Controls */
        .controls-card {{
            background-color: var(--bg-card);
            backdrop-filter: var(--glass-blur);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 16px 20px;
            margin-bottom: 24px;
            box-shadow: var(--shadow-sm);
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
        }}

        .search-wrapper {{
            position: relative;
            flex-grow: 1;
            max-width: 400px;
        }}

        .search-wrapper i {{
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-secondary);
            font-size: 14px;
        }}

        .search-input {{
            width: 100%;
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 10px 14px 10px 38px;
            border-radius: var(--radius-sm);
            font-size: 14px;
            outline: none;
        }}

        .search-input:focus {{
            border-color: var(--accent-primary);
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
        }}

        .filter-group {{
            display: flex;
            gap: 12px;
            align-items: center;
        }}

        .filter-select {{
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 9px 14px;
            border-radius: var(--radius-sm);
            font-size: 14px;
            outline: none;
            cursor: pointer;
        }}

        /* Table Card Styling */
        .table-card {{
            background-color: var(--bg-card);
            backdrop-filter: var(--glass-blur);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-md);
            overflow: hidden;
            margin-bottom: 32px;
        }}

        .table-wrapper {{
            overflow-x: auto;
            max-height: 600px;
            overflow-y: auto;
        }}

        .custom-table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 14px;
        }}

        .custom-table th {{
            background-color: var(--bg-secondary);
            color: var(--text-secondary);
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            padding: 14px 20px;
            border-bottom: 1px solid var(--border-color);
            position: sticky;
            top: 0;
            z-index: 10;
        }}

        .custom-table td {{
            padding: 14px 20px;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-primary);
        }}

        .custom-table tbody tr {{
            cursor: pointer;
        }}

        .custom-table tbody tr:hover {{
            background-color: rgba(255, 255, 255, 0.02);
        }}
        
        .light-theme .custom-table tbody tr:hover {{
            background-color: rgba(0, 0, 0, 0.01);
        }}

        /* Badges */
        .badge {{
            display: inline-flex;
            align-items: center;
            padding: 4px 8px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 500;
            font-family: 'Outfit', sans-serif;
        }}

        .badge-primary {{
            background-color: rgba(99, 102, 241, 0.1);
            color: var(--accent-primary);
        }}

        .badge-success {{
            background-color: rgba(16, 185, 129, 0.1);
            color: var(--success);
        }}

        .badge-gray {{
            background-color: rgba(156, 163, 175, 0.1);
            color: var(--text-secondary);
        }}

        /* Buttons */
        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            border-radius: var(--radius-sm);
            font-family: 'Outfit', sans-serif;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            border: 1px solid transparent;
            text-decoration: none;
            outline: none;
        }}

        .btn-primary {{
            background: var(--accent-gradient);
            color: white;
            box-shadow: var(--shadow-accent);
        }}

        .btn-primary:hover {{
            opacity: 0.95;
        }}

        .btn-outline {{
            background: transparent;
            border: 1px solid var(--border-color);
            color: var(--text-primary);
        }}

        .btn-outline:hover {{
            background-color: var(--border-color);
        }}

        /* Tabs Panes */
        .tab-pane {{
            display: none;
        }}

        .tab-pane.active {{
            display: block;
        }}

        /* Cards Grid */
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 20px;
            margin-bottom: 32px;
        }}

        .interactive-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 24px;
            box-shadow: var(--shadow-sm);
            cursor: pointer;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        .interactive-card:hover {{
            border-color: var(--accent-primary);
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }}

        .card-header-flex {{
            display: flex;
            justify-content: space-between;
            align-items: start;
        }}

        .card-title {{
            font-size: 18px;
            font-weight: 600;
            line-height: 1.3;
        }}

        .card-meta {{
            font-size: 13px;
            color: var(--text-secondary);
        }}

        /* Modal / Detail Drawer styling */
        .drawer-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(4px);
            z-index: 100;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }}

        .drawer-overlay.active {{
            opacity: 1;
            pointer-events: auto;
        }}

        .detail-drawer {{
            position: fixed;
            top: 0;
            right: -500px;
            width: 500px;
            height: 100vh;
            background-color: var(--bg-secondary);
            border-left: 1px solid var(--border-color);
            z-index: 101;
            box-shadow: var(--shadow-lg);
            display: flex;
            flex-direction: column;
            transition: right 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            padding: 32px;
        }}

        .detail-drawer.active {{
            right: 0;
        }}

        .drawer-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 24px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 16px;
        }}

        .drawer-close {{
            background: transparent;
            border: none;
            font-size: 20px;
            color: var(--text-secondary);
            cursor: pointer;
        }}

        .drawer-close:hover {{
            color: var(--text-primary);
        }}

        .drawer-body {{
            overflow-y: auto;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}

        .drawer-section-title {{
            font-size: 14px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            margin-bottom: 8px;
        }}

        .citation-item {{
            padding: 12px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-color);
            margin-bottom: 10px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .citation-item:hover {{
            border-color: var(--accent-primary);
        }}

        .citation-item.highlighted-citation {{
            border-color: var(--accent-primary);
            background-color: rgba(99, 102, 241, 0.12);
            box-shadow: 0 0 10px rgba(99, 102, 241, 0.2);
            transform: scale(1.02);
            transition: all 0.2s ease;
        }}
        .light-theme .citation-item.highlighted-citation {{
            background-color: rgba(79, 70, 229, 0.08);
        }}
    </style>
</head>
<body>
    <div class="app-container">
        <!-- Sidebar Navigation -->
        <aside class="sidebar">
            <div class="brand-section">
                <div class="brand-icon"><i class="fa-solid fa-brain"></i></div>
                <div>
                    <h1 class="brand-title">Patent Intelligence</h1>
                    <p style="font-size: 10px; color: var(--text-secondary);">James McKeeth Portfolio</p>
                </div>
            </div>
            
            <nav>
                <ul class="nav-menu">
                    <li class="nav-item active" data-tab="overview">
                        <button><i class="fa-solid fa-chart-line"></i>Overview</button>
                    </li>
                    <li class="nav-item" data-tab="my-patents">
                        <button><i class="fa-solid fa-file-invoice"></i>My Patents</button>
                    </li>
                    <li class="nav-item" data-tab="citations">
                        <button><i class="fa-solid fa-arrows-split-up-and-left"></i>Citations</button>
                    </li>
                    <li class="nav-item" data-tab="companies">
                        <button><i class="fa-solid fa-building"></i>Citing Companies</button>
                    </li>
                    <li class="nav-item" data-tab="families">
                        <button><i class="fa-solid fa-folder-tree"></i>Patent Families</button>
                    </li>
                </ul>
            </nav>
            
            <div class="sidebar-footer">
                <span style="font-size: 12px; color: var(--text-secondary);">v2.0 Stably Sorted</span>
                <button class="theme-toggle-btn" id="themeToggle"><i class="fa-solid fa-sun"></i></button>
            </div>
        </aside>

        <!-- Main Content Panel -->
        <main class="main-content">
            <header class="header-section">
                <div>
                    <h1 class="header-title" id="pageTitle">Executive Overview</h1>
                    <p class="header-subtitle" id="pageSubtitle">Key statistics and performance of the patent portfolio</p>
                </div>
            </header>

            <!-- Dashboard Overview Panel (Default Pane) -->
            <div id="overviewPane" class="tab-pane active">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon"><i class="fa-solid fa-passport"></i></div>
                        <div class="stat-info">
                            <span class="stat-value" id="statPortfolioCount">0</span>
                            <span class="stat-label">Portfolio Patents</span>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon"><i class="fa-solid fa-users"></i></div>
                        <div class="stat-info">
                            <span class="stat-value" id="statUniqueCiters">0</span>
                            <span class="stat-label">Unique Citing Patents</span>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon"><i class="fa-solid fa-link"></i></div>
                        <div class="stat-info">
                            <span class="stat-value" id="statTotalCitations">0</span>
                            <span class="stat-label">Total Citations</span>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon"><i class="fa-solid fa-circle-check"></i></div>
                        <div class="stat-info">
                            <span class="stat-value">100%</span>
                            <span class="stat-label">Family Citation Rate</span>
                        </div>
                    </div>
                </div>

                <div class="cards-grid">
                    <div class="interactive-card" onclick="switchTab('my-patents')">
                        <div class="card-header-flex">
                            <h3 class="card-title">Patent Portfolio Explorer</h3>
                            <i class="fa-solid fa-circle-arrow-right" style="color: var(--accent-primary);"></i>
                        </div>
                        <p class="card-meta">View all 62 authored publications, divisional releases, and details. Link directly to locally stored PDFs.</p>
                    </div>
                    <div class="interactive-card" onclick="switchTab('citations')">
                        <div class="card-header-flex">
                            <h3 class="card-title">Citations Mapping</h3>
                            <i class="fa-solid fa-circle-arrow-right" style="color: var(--accent-primary);"></i>
                        </div>
                        <p class="card-meta">Search through 1,032 forward citations, categories (Applicant, Examiner), and URLs.</p>
                    </div>
                    <div class="interactive-card" onclick="switchTab('companies')">
                        <div class="card-header-flex">
                            <h3 class="card-title">Company Analytics</h3>
                            <i class="fa-solid fa-circle-arrow-right" style="color: var(--accent-primary);"></i>
                        </div>
                        <p class="card-meta">Examine corporate assignees citing the portfolio, led by Micron, Google, IBM, Apple, and Microsoft.</p>
                    </div>
                </div>
                
                <div class="table-card">
                    <div style="padding: 20px; border-bottom: 1px solid var(--border-color); font-weight: 600;">
                        Top Cited Individual Patents
                    </div>
                    <div class="table-wrapper">
                        <table class="custom-table" id="topCitedOverviewTable">
                            <thead>
                                <tr>
                                    <th>Document ID</th>
                                    <th>Citations</th>
                                    <th>Patent Title</th>
                                    <th>Representative Family ID</th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- Dynamic JS -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- My Patents Panel -->
            <div id="myPatentsPane" class="tab-pane">
                <div class="controls-card">
                    <div class="search-wrapper">
                        <i class="fa-solid fa-magnifying-glass"></i>
                        <input type="text" class="search-input" id="searchMyPatents" placeholder="Search ID, Title, or CPC...">
                    </div>
                    <div class="filter-group">
                        <select class="filter-select" id="filterMyFamily">
                            <option value="">All Families</option>
                            <!-- Dynamic JS -->
                        </select>
                    </div>
                </div>

                <div class="table-card">
                    <div class="table-wrapper">
                        <table class="custom-table" id="myPatentsTable">
                            <thead>
                                <tr>
                                    <th>Document ID</th>
                                    <th>Title</th>
                                    <th>Published</th>
                                    <th>Family ID</th>
                                    <th>Pages</th>
                                    <th>CPCI Code</th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- Dynamic JS -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Citations Panel -->
            <div id="citationsPane" class="tab-pane">
                <div class="controls-card">
                    <div class="search-wrapper">
                        <i class="fa-solid fa-magnifying-glass"></i>
                        <input type="text" class="search-input" id="searchCitations" placeholder="Search Citing ID, Title, Assignee...">
                    </div>
                    <div class="filter-group">
                        <select class="filter-select" id="filterCategory">
                            <option value="">All Categories</option>
                            <!-- Dynamic JS -->
                        </select>
                    </div>
                </div>

                <div class="table-card">
                    <div class="table-wrapper">
                        <table class="custom-table" id="citationsTable">
                            <thead>
                                <tr>
                                    <th>Citing Patent</th>
                                    <th>Citing Assignee</th>
                                    <th>Cited Patent</th>
                                    <th>Citing Title</th>
                                    <th>Category</th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- Dynamic JS -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Citing Companies Panel -->
            <div id="companiesPane" class="tab-pane">
                <div class="cards-grid" id="companiesGrid">
                    <!-- Dynamic JS -->
                </div>
                
                <div class="table-card" id="companySpecificTableCard" style="display: none;">
                    <div style="padding: 20px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center;">
                        <span id="companyTableTitle" style="font-weight: 600;">Company Citations</span>
                        <button class="btn btn-outline" style="padding: 4px 8px; font-size: 11px;" onclick="clearCompanyFilter()">Show All Companies</button>
                    </div>
                    <div class="table-wrapper">
                        <table class="custom-table" id="companySpecificTable">
                            <thead>
                                <tr>
                                    <th>Citing Patent</th>
                                    <th>Citing Title</th>
                                    <th>Cited Patent ID</th>
                                    <th>Cited Patent Title</th>
                                    <th>Category</th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- Dynamic JS -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Patent Families Panel -->
            <div id="familiesPane" class="tab-pane">
                <div class="cards-grid" id="familiesGrid">
                    <!-- Dynamic JS -->
                </div>
            </div>
        </main>
    </div>

    <!-- Details Overlay Panel Drawer -->
    <div class="drawer-overlay" id="drawerOverlay" onclick="closeDrawer()"></div>
    <div class="detail-drawer" id="detailDrawer">
        <div class="drawer-header">
            <div>
                <h2 id="drawerTitle" style="font-size: 20px; margin-bottom: 4px;">Patent Details</h2>
                <span id="drawerDocId" class="badge badge-primary">US-0000000-A0</span>
            </div>
            <button class="drawer-close" onclick="closeDrawer()"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <div class="drawer-body">
            <div>
                <div class="drawer-section-title">Patent Title</div>
                <div id="drawerFullTitle" style="font-weight: 500; font-size: 15px;">-</div>
            </div>
            
            <div style="display: flex; gap: 24px;">
                <div>
                    <div class="drawer-section-title">Published Date</div>
                    <div id="drawerDate">-</div>
                </div>
                <div>
                    <div class="drawer-section-title">Family ID</div>
                    <div id="drawerFamily">-</div>
                </div>
                <div>
                    <div class="drawer-section-title">Page Count</div>
                    <div id="drawerPages">-</div>
                </div>
            </div>

            <div>
                <div class="drawer-section-title">CPCI Classes</div>
                <div id="drawerCPC" style="font-family: monospace; font-size: 13px; word-break: break-all;">-</div>
            </div>

            <div style="display: flex; gap: 12px; margin: 8px 0 16px;">
                <a id="drawerBtnWeb" href="#" class="btn btn-primary" style="flex-grow: 1; justify-content: center;" target="_blank"><i class="fa-solid fa-arrow-up-right-from-square"></i> View on Google Patents</a>
            </div>

            <div>
                <div class="drawer-section-title" id="drawerCitationHeader">Forward Citations (0)</div>
                <div id="drawerCitationsList" style="max-height: 300px; overflow-y: auto;">
                    <!-- Dynamic JS -->
                </div>
            </div>
        </div>
    </div>

    <!-- Data Injection -->
    <script id="patentData" type="application/json">
{json_data}
    </script>

    <!-- App Logic -->
    <script>
        // Load data from the injected payload
        const data = JSON.parse(document.getElementById('patentData').textContent);
        
        let currentTab = 'overview';
        let companyFilter = '';

        // Initialize App
        function init() {{
            setupNavigation();
            setupTheme();
            renderStats();
            renderTopCitedOverview();
            renderMyPatents();
            renderCitations();
            renderCompanies();
            renderFamilies();
            setupSearchFilters();
        }}

        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', init);
        }} else {{
            init();
        }}

        function setupTheme() {{
            const themeToggle = document.getElementById('themeToggle');
            const htmlElement = document.documentElement;
            
            themeToggle.addEventListener('click', () => {{
                if (htmlElement.classList.contains('dark-theme')) {{
                    htmlElement.classList.replace('dark-theme', 'light-theme');
                    themeToggle.innerHTML = '<i class="fa-solid fa-moon"></i>';
                }} else {{
                    htmlElement.classList.replace('light-theme', 'dark-theme');
                    themeToggle.innerHTML = '<i class="fa-solid fa-sun"></i>';
                }}
            }});
        }}

        function setupNavigation() {{
            const navItems = document.querySelectorAll('.nav-item');
            navItems.forEach(item => {{
                item.addEventListener('click', () => {{
                    const tabId = item.getAttribute('data-tab');
                    switchTab(tabId);
                }});
            }});
        }}

        function switchTab(tabId) {{
            // Deactivate current active nav/pane
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
            
            // Activate target nav/pane
            const targetNav = document.querySelector(`.nav-item[data-tab="${{tabId}}"]`);
            if (targetNav) targetNav.classList.add('active');
            
            // Scroll main content to top
            const mainContent = document.querySelector('.main-content');
            if (mainContent) {{
                mainContent.scrollTop = 0;
            }}
            
            const targetPane = document.getElementById(`${{
                tabId === 'overview' ? 'overviewPane' :
                tabId === 'my-patents' ? 'myPatentsPane' :
                tabId === 'citations' ? 'citationsPane' :
                tabId === 'companies' ? 'companiesPane' : 'familiesPane'
            }}`);
            if (targetPane) targetPane.classList.add('active');
            
            // Set header labels
            const titleEl = document.getElementById('pageTitle');
            const subtitleEl = document.getElementById('pageSubtitle');
            
            if (tabId === 'overview') {{
                titleEl.textContent = 'Executive Overview';
                subtitleEl.textContent = 'Key statistics and performance of the patent portfolio';
            }} else if (tabId === 'my-patents') {{
                titleEl.textContent = 'My Patents';
                subtitleEl.textContent = 'Authored publications and divisionals with local PDF access';
            }} else if (tabId === 'citations') {{
                titleEl.textContent = 'Forward Citations Mapping';
                subtitleEl.textContent = 'Full list of 1,032 citation links showing how others reference your work';
            }} else if (tabId === 'companies') {{
                titleEl.textContent = 'Citing Corporations';
                subtitleEl.textContent = 'Analyzing corporate entities citing your patent portfolio';
            }} else if (tabId === 'families') {{
                titleEl.textContent = 'Patent Families';
                subtitleEl.textContent = 'Reviewing citation rates across the 12 core invention families';
            }}
            
            currentTab = tabId;
            closeDrawer();
        }}

        function renderStats() {{
            document.getElementById('statPortfolioCount').textContent = data.myPatents.length;
            
            // Count unique citing patents
            const uniqueCiters = new Set(data.forwardCitations.map(c => c.citing_patent));
            document.getElementById('statUniqueCiters').textContent = uniqueCiters.size;
            document.getElementById('statTotalCitations').textContent = data.forwardCitations.length;
        }}

        function renderTopCitedOverview() {{
            const tbody = document.querySelector('#topCitedOverviewTable tbody');
            tbody.innerHTML = '';
            
            // Count citations per cited patent using normalized IDs
            const counts = {{}};
            data.forwardCitations.forEach(c => {{
                counts[c.cited_patent_normalized] = (counts[c.cited_patent_normalized] || 0) + 1;
            }});
            
            // Sort
            const sorted = Object.entries(counts).sort((a,b) => b[1] - a[1]).slice(0, 5);
            
            sorted.forEach(([docId, count]) => {{
                // Find patent metadata
                const pat = data.myPatents.find(p => p.id_normalized === docId);
                const displayId = pat ? pat['Document ID'] : docId;
                const title = pat ? pat.Title : 'Unknown';
                const familyId = pat ? pat['Family ID'] : 'Unknown';
                
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong style="color: var(--accent-primary);">${{displayId}}</strong></td>
                    <td><span class="badge badge-primary" style="font-weight:bold;">${{count}} citations</span></td>
                    <td>${{title}}</td>
                    <td><span class="badge badge-gray">${{familyId}}</span></td>
                `;
                tr.addEventListener('click', () => openPatentDetails(docId));
                tbody.appendChild(tr);
            }});
        }}

        function renderMyPatents() {{
            const tbody = document.querySelector('#myPatentsTable tbody');
            const selectFilter = document.getElementById('filterMyFamily');
            tbody.innerHTML = '';
            
            // Populate families filter select
            const families = [...new Set(data.myPatents.map(p => p['Family ID']))].sort();
            selectFilter.innerHTML = '<option value="">All Families</option>';
            families.forEach(f => {{
                selectFilter.innerHTML += `<option value="${{f}}">Family ${{f}}</option>`;
            }});
            
            data.myPatents.forEach(p => {{
                const tr = document.createElement('tr');
                tr.setAttribute('data-id', p.id_normalized);
                tr.innerHTML = `
                    <td><strong style="color: var(--accent-primary);">${{p['Document ID']}}</strong></td>
                    <td style="font-weight: 500;">${{p.Title}}</td>
                    <td>${{p['Date Published']}}</td>
                    <td><span class="badge badge-gray">${{p['Family ID']}}</span></td>
                    <td>${{p.Pages}}</td>
                    <td style="font-family: monospace; font-size: 12px; color: var(--text-secondary);">${{p.CPCI ? p.CPCI.substring(0, 25) + '...' : '-'}}</td>
                `;
                tr.addEventListener('click', () => openPatentDetails(p.id_normalized));
                tbody.appendChild(tr);
            }});
        }}

        function renderCitations() {{
            const tbody = document.querySelector('#citationsTable tbody');
            const selectFilter = document.getElementById('filterCategory');
            tbody.innerHTML = '';
            
            // Populate category select
            const categories = [...new Set(data.forwardCitations.map(c => c.category_name))].sort();
            selectFilter.innerHTML = '<option value="">All Categories</option>';
            categories.forEach(c => {{
                if(c) selectFilter.innerHTML += `<option value="${{c}}">${{c}}</option>`;
            }});
            
            data.forwardCitations.forEach(c => {{
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong style="color: var(--text-primary);">${{c.citing_patent}}</strong></td>
                    <td style="font-weight: 500;">${{c.citing_assignee || 'Unknown'}}</td>
                    <td><span class="badge badge-primary">${{c.cited_patent}}</span></td>
                    <td style="color: var(--text-secondary);">${{c.citing_title || '-'}}</td>
                    <td><span class="badge badge-gray">${{c.category_name || c.category_code || '-'}}</span></td>
                `;
                tr.addEventListener('click', () => openPatentDetails(c.cited_patent_normalized, c.citing_patent));
                tbody.appendChild(tr);
            }});
        }}

        function renderCompanies() {{
            const grid = document.getElementById('companiesGrid');
            grid.innerHTML = '';
            
            // Exlode assignees and count
            const companyCounts = {{}};
            const companyPatents = {{}};
            
            data.forwardCitations.forEach(c => {{
                if (!c.citing_assignee) return;
                const list = c.citing_assignee.split(', ');
                list.forEach(comp => {{
                    companyCounts[comp] = (companyCounts[comp] || 0) + 1;
                    if(!companyPatents[comp]) companyPatents[comp] = new Set();
                    companyPatents[comp].add(c.citing_patent);
                }});
            }});
            
            // Sort
            const sorted = Object.entries(companyCounts).sort((a,b) => b[1] - a[1]).slice(0, 9);
            
            sorted.forEach(([comp, count]) => {{
                const uniquePats = companyPatents[comp].size;
                const card = document.createElement('div');
                card.className = 'interactive-card';
                card.innerHTML = `
                    <div class="card-header-flex">
                        <h3 class="card-title" style="font-size: 16px;">${{comp}}</h3>
                        <i class="fa-solid fa-building" style="color: var(--accent-primary);"></i>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-top:8px;">
                        <span class="stat-label">Citations Links</span>
                        <strong style="color: var(--accent-primary);">${{count}}</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between;">
                        <span class="stat-label">Unique Patents</span>
                        <strong>${{uniquePats}}</strong>
                    </div>
                `;
                card.addEventListener('click', () => showCompanyCitationsTable(comp));
                grid.appendChild(card);
            }});
        }}

        function showCompanyCitationsTable(company) {{
            companyFilter = company;
            const cardTable = document.getElementById('companySpecificTableCard');
            const tableTitle = document.getElementById('companyTableTitle');
            const tbody = document.querySelector('#companySpecificTable tbody');
            
            tableTitle.textContent = `Patent Citations by: ${{company}}`;
            tbody.innerHTML = '';
            
            // Filter citations by company
            const filtered = data.forwardCitations.filter(c => {{
                return c.citing_assignee && c.citing_assignee.split(', ').includes(company);
            }});
            
            filtered.forEach(c => {{
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${{c.citing_patent}}</strong></td>
                    <td>${{c.citing_title || '-'}}</td>
                    <td><span class="badge badge-primary">${{c.cited_patent}}</span></td>
                    <td style="color: var(--text-secondary);">${{c.cited_title || '-'}}</td>
                    <td><span class="badge badge-gray">${{c.category_name || c.category_code}}</span></td>
                `;
                tr.addEventListener('click', () => openPatentDetails(c.cited_patent_normalized, c.citing_patent));
                tbody.appendChild(tr);
            }});
            
            cardTable.style.display = 'block';
            cardTable.scrollIntoView({{ behavior: 'smooth' }});
        }}

        function clearCompanyFilter() {{
            companyFilter = '';
            document.getElementById('companySpecificTableCard').style.display = 'none';
        }}

        function renderFamilies() {{
            const grid = document.getElementById('familiesGrid');
            grid.innerHTML = '';
            
            // Group patents by family
            const familyMembers = {{}};
            data.myPatents.forEach(p => {{
                const fid = p['Family ID'];
                if(!familyMembers[fid]) familyMembers[fid] = [];
                familyMembers[fid].push(p);
            }});
            
            // Count citations per family ID
            const familyCitations = {{}};
            data.forwardCitations.forEach(c => {{
                if (c.cited_family_id) {{
                    familyCitations[c.cited_family_id] = (familyCitations[c.cited_family_id] || 0) + 1;
                }}
            }});
            
            // Render family cards
            Object.entries(familyMembers).forEach(([fid, members]) => {{
                const count = familyCitations[fid] || 0;
                
                // Get representative titles
                const titles = [...new Set(members.map(m => m.Title))];
                const repTitle = titles[0];
                
                const card = document.createElement('div');
                card.className = 'interactive-card';
                card.innerHTML = `
                    <div class="card-header-flex">
                        <span class="badge badge-primary">Family ${{fid}}</span>
                        <span class="badge badge-success" style="font-weight:bold;">${{count}} citations</span>
                    </div>
                    <h3 class="card-title" style="font-size: 15px; margin-top:8px;">${{repTitle}}</h3>
                    <p style="font-size: 12px; color: var(--text-secondary);">${{members.length}} portfolio publications in this family.</p>
                `;
                card.addEventListener('click', () => {{
                    switchTab('my-patents');
                    document.getElementById('filterMyFamily').value = fid;
                    filterMyPatentsTable();
                }});
                grid.appendChild(card);
            }});
        }}

        function setupSearchFilters() {{
            // My Patents search
            document.getElementById('searchMyPatents').addEventListener('input', filterMyPatentsTable);
            document.getElementById('filterMyFamily').addEventListener('change', filterMyPatentsTable);
            
            // Citations search
            document.getElementById('searchCitations').addEventListener('input', filterCitationsTable);
            document.getElementById('filterCategory').addEventListener('change', filterCitationsTable);
        }}

        function filterMyPatentsTable() {{
            const q = document.getElementById('searchMyPatents').value.toLowerCase();
            const fid = document.getElementById('filterMyFamily').value;
            const rows = document.querySelectorAll('#myPatentsTable tbody tr');
            
            rows.forEach(row => {{
                const patId = row.getAttribute('data-id');
                const pat = data.myPatents.find(p => p.id_normalized === patId);
                
                const matchSearch = !q || 
                    pat['Document ID'].toLowerCase().includes(q) || 
                    pat.Title.toLowerCase().includes(q) || 
                    (pat.CPCI && pat.CPCI.toLowerCase().includes(q));
                    
                const matchFamily = !fid || pat['Family ID'].toString() === fid;
                
                if(matchSearch && matchFamily) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }});
        }}

        function filterCitationsTable() {{
            const q = document.getElementById('searchCitations').value.toLowerCase();
            const cat = document.getElementById('filterCategory').value;
            const rows = document.querySelectorAll('#citationsTable tbody tr');
            
            rows.forEach(row => {{
                // Extract cells content
                const cells = row.getElementsByTagName('td');
                const citerId = cells[0].textContent.toLowerCase();
                const citerAssignee = cells[1].textContent.toLowerCase();
                const citedId = cells[2].textContent.toLowerCase();
                const citerTitle = cells[3].textContent.toLowerCase();
                const category = cells[4].textContent;
                
                const matchSearch = !q || 
                    citerId.includes(q) || 
                    citerAssignee.includes(q) || 
                    citedId.includes(q) || 
                    citerTitle.includes(q);
                    
                const matchCategory = !cat || category === cat;
                
                if(matchSearch && matchCategory) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }});
        }}

        // Detail Drawer Actions
        function openPatentDetails(docId, highlightCiterId) {{
            const pat = data.myPatents.find(p => p.id_normalized === docId);
            if (!pat) return;
            
            document.getElementById('drawerDocId').textContent = pat['Document ID'];
            document.getElementById('drawerFullTitle').textContent = pat.Title;
            document.getElementById('drawerDate').textContent = pat['Date Published'] || '-';
            document.getElementById('drawerFamily').textContent = pat['Family ID'] || '-';
            document.getElementById('drawerPages').textContent = pat.Pages || '-';
            document.getElementById('drawerCPC').textContent = pat.CPCI || 'None';
            
            // Setup Google Patents Link
            const webBtn = document.getElementById('drawerBtnWeb');
            const googlePatId = pat['Document ID'].replace(/[- ]/g, '');
            webBtn.href = `https://patents.google.com/patent/${{googlePatId}}/en`;
            
            // Populate forward citations list for this specific patent using normalized IDs
            const citations = data.forwardCitations.filter(c => c.cited_patent_normalized === docId);
            const citeHeader = document.getElementById('drawerCitationHeader');
            citeHeader.textContent = `Forward Citations (${{citations.length}})`;
            
            const citeList = document.getElementById('drawerCitationsList');
            citeList.innerHTML = '';
            
            if(citations.length === 0) {{
                citeList.innerHTML = '<div style="color: var(--text-secondary); text-align:center; padding: 20px 0;">No forward citations found for this patent.</div>';
            }} else {{
                citations.forEach(c => {{
                    const isHighlighted = (c.citing_patent === highlightCiterId);
                    const highlightClass = isHighlighted ? ' highlighted-citation' : '';
                    const highlightId = isHighlighted ? ' id="highlightedCitationItem"' : '';
                    
                    citeList.innerHTML += `
                        <div class="citation-item${{highlightClass}}"${{highlightId}}>
                            <div style="display:flex; justify-content:space-between; align-items:start;">
                                <strong style="font-size:13px; color:var(--accent-primary);">${{c.citing_patent}}</strong>
                                <span class="badge badge-gray" style="font-size:10px; padding:2px 6px;">${{c.category_name || c.category_code}}</span>
                            </div>
                            <div style="font-size:12px; font-weight:500; margin-top:2px;">${{c.citing_title || '-'}}</div>
                            <div style="font-size:11px; color:var(--text-secondary); margin-top:2px;">
                                <i class="fa-solid fa-building"></i> ${{c.citing_assignee || 'Unknown Assignee'}}
                            </div>
                            <a href="${{c.citing_url}}" target="_blank" style="font-size:11px; color:var(--accent-primary); text-decoration:none; margin-top:4px; display:inline-block;">
                                <i class="fa-solid fa-arrow-up-right-from-square"></i> View on Google Patents
                            </a>
                        </div>
                    `;
                }});
            }}
            
            // Open Drawer
            document.getElementById('drawerOverlay').classList.add('active');
            document.getElementById('detailDrawer').classList.add('active');

            // Scroll highlighted citation into view if applicable
            if (highlightCiterId) {{
                const highlightEl = document.getElementById('highlightedCitationItem');
                if (highlightEl) {{
                    setTimeout(() => {{
                        highlightEl.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                    }}, 200);
                }}
            }}
        }}

        function closeDrawer() {{
            document.getElementById('drawerOverlay').classList.remove('active');
            document.getElementById('detailDrawer').classList.remove('active');
        }}
    </script>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"Success! Generated {output_path}")

if __name__ == "__main__":
    main()
