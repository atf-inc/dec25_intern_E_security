// Comprehensive translations for English and Japanese

export type Language = 'en' | 'ja';

export interface Translations {
  // Common
  common: {
    shadowGuard: string;
    login: string;
    logout: string;
    loading: string;
    error: string;
    success: string;
    view: string;
    close: string;
    apply: string;
    clearAll: string;
    filter: string;
    filters: string;
    filterActive: string;
    filtersActive: string;
  };
  
  // Landing Page
  landing: {
    // Hero Section
    heroTitle: string;
    heroSubtitle: string;
    launchSimulation: string;
    viewDashboard: string;
    
    // Problem Section
    theProblem: string;
    problemTitle: string;
    problemTitleHighlight: string;
    problemSubtitle: string;
    
    // Threat Cards
    dataLogAnalysis: string;
    logsProcessed: string;
    realTimeDataStream: string;
    threats: string;
    aiScans: string;
    users: string;
    saasApps: string;
    live: string;
    
    // Problem List
    threat1Title: string;
    threat1Desc: string;
    threat2Title: string;
    threat2Desc: string;
    threat3Title: string;
    threat3Desc: string;
    threat4Title: string;
    threat4Desc: string;
    
    // Solution Section
    solutionTitle: string;
    solutionTitleHighlight: string;
    solutionSubtitle: string;
    
    // Solution Cards
    solution1Title: string;
    solution1Desc: string;
    solution1Note: string;
    solution2Title: string;
    solution2Desc: string;
    solution2Note: string;
    solution3Title: string;
    solution3Desc: string;
    solution3Note: string;
    
    // Simulation Section
    testDefenseGrid: string;
    defenseGridHighlight: string;
    simulationSubtitle: string;
    
    // Architecture Section
    systemArchitecture: string;
    architectureHighlight: string;
    logs: string;
    collector: string;
    redis: string;
    worker: string;
    dashboard: string;
    
    // Footer
    githubRepo: string;
    apiDocs: string;
    teamCredits: string;
    footerCopyright: string;
  };
  
  // Dashboard
  dashboard: {
    securityOverview: string;
    securityOverviewSubtitle: string;
    totalAlerts: string;
    highRisk: string;
    affectedUsers: string;
    avgRiskScore: string;
    recentAlerts: string;
    syncing: string;
    liveStatus: string;
    
    // Table Headers
    time: string;
    user: string;
    domain: string;
    category: string;
    risk: string;
    status: string;
    action: string;
    
    // Status Labels
    statusNew: string;
    statusInvestigating: string;
    statusResolved: string;
    
    // Risk Levels
    riskHigh: string;
    riskMedium: string;
    riskLow: string;
    
    // Modal
    aiAnalysis: string;
    alertMetadata: string;
    riskScore: string;
    timestamp: string;
    rawLog: string;
    markInvestigating: string;
    resolve: string;
    
    // Messages
    loadingAlerts: string;
    failedToLoad: string;
    failedToLoadDesc: string;
    allClear: string;
    allClearDesc: string;
    justNow: string;
    minsAgo: string;
    hoursAgo: string;
    daysAgo: string;
  };
  
  // Login Page
  login: {
    secureDashboardAccess: string;
    signInWithGoogle: string;
    connectingToGoogle: string;
  };
  
  // Simulation Console
  simulation: {
    defenseGridConsole: string;
    simulateShadowAI: string;
    simulateDataLeak: string;
    simulateSafeTraffic: string;
    testSlackAlert: string;
    viewDashboardBtn: string;
    viewDocumentation: string;
    
    // Console Messages
    readyToRun: string;
    initializingSimulation: string;
    injectingPayload: string;
    workerReceived: string;
    runningAnalysis: string;
    simulationSent: string;
    expectedRisk: string;
    checkDashboard: string;
    clearedPreviousAlerts: string;
    simulationStarted: string;
    simulationInitiated: string;
    
    // Type Labels
    shadowAI: string;
    dataLeakBlacklist: string;
    safeTrafficWhitelist: string;
    
    // Toast
    simulationSentOpening: string;
    slackAlertSent: string;
  };
  
  // Filter Panel
  filterPanel: {
    filterOptions: string;
    riskLevel: string;
    timeRange: string;
    eventCategory: string;
    applyFilters: string;
    
    // Risk Levels
    highRisk: string;
    mediumRisk: string;
    lowRisk: string;
    
    // Time Ranges
    lastHour: string;
    last24Hours: string;
    last7Days: string;
    last30Days: string;
    allTime: string;
    
    // Categories
    normalEvents: string;
    shadowIT: string;
    blacklistedServices: string;
  };
  
  // Language Toggle
  languageToggle: {
    english: string;
    japanese: string;
    switchLanguage: string;
  };
}

export const translations: Record<Language, Translations> = {
  en: {
    common: {
      shadowGuard: 'ShadowGuard',
      login: 'Login',
      logout: 'Logout',
      loading: 'Loading...',
      error: 'Error',
      success: 'Success',
      view: 'View',
      close: 'Close',
      apply: 'Apply',
      clearAll: 'Clear all',
      filter: 'Filter',
      filters: 'filters',
      filterActive: 'filter active',
      filtersActive: 'filters active',
    },
    landing: {
      heroTitle: 'Detect Shadow IT',
      heroSubtitle: 'Real-time detection of unauthorized SaaS usage, Shadow AI, and file sharing in your corporate network.',
      launchSimulation: 'Launch Simulation',
      viewDashboard: 'View Dashboard',
      
      theProblem: 'The Problem',
      problemTitle: 'New AI workflows equal ',
      problemTitleHighlight: 'New Threats',
      problemSubtitle: 'Compromising AI Supply Chains. Employees unknowingly expose sensitive data through unapproved AI tools and shadow SaaS applications.',
      
      dataLogAnalysis: 'Data Log Analysis',
      logsProcessed: 'Logs Processed:',
      realTimeDataStream: 'Real-time data stream active',
      threats: 'Threats',
      aiScans: 'AI Scans',
      users: 'Users',
      saasApps: 'SaaS Apps',
      live: 'Live',
      
      threat1Title: 'Unchecked Shadow AI Usage',
      threat1Desc: 'Employees pasting sensitive code and PII into unapproved public LLMs.',
      threat2Title: 'Unauthorized Data Exfiltration',
      threat2Desc: 'Silent uploads of corporate IP to file-sharing services like Mega.',
      threat3Title: 'Bypassing Legacy Firewalls',
      threat3Desc: 'Encrypted SaaS traffic often evades traditional inspection tools.',
      threat4Title: 'Lack of Semantic Visibility',
      threat4Desc: 'Security teams lack context on why a user accessed a site.',
      
      solutionTitle: 'Complete Visibility into ',
      solutionTitleHighlight: 'Shadow AI',
      solutionSubtitle: 'Detect, Analyze, and Block unauthorized GenAI usage before data leaves your network.',
      
      solution1Title: 'Real-Time Interception',
      solution1Desc: 'Collector Engine ingests logs instantly from any source (Zscaler, Firewalls)',
      solution1Note: 'What data goes into an AI workflow',
      solution2Title: 'AI-Powered Analysis',
      solution2Desc: 'OpenRouter LLM semantic analysis understands context, not just keywords',
      solution2Note: 'What code is run and where it is executed',
      solution3Title: 'Instant Response',
      solution3Desc: 'Automated Slack alerts and Dashboard visualizations in milliseconds',
      solution3Note: 'The output is genuine and secure',
      
      testDefenseGrid: 'Test the ',
      defenseGridHighlight: 'Defense Grid',
      simulationSubtitle: 'Run live simulations against our AI engine right now.',
      
      systemArchitecture: 'System ',
      architectureHighlight: 'Architecture',
      logs: 'Logs',
      collector: 'Collector',
      redis: 'Redis',
      worker: 'Worker',
      dashboard: 'Dashboard',
      
      githubRepo: 'GitHub Repo',
      apiDocs: 'API Docs',
      teamCredits: 'Team Credits',
      footerCopyright: '© 2025 ShadowGuard. Securing the Agentic AI Era.',
    },
    dashboard: {
      securityOverview: 'Security Overview',
      securityOverviewSubtitle: 'Real-time monitoring of shadow IT activities in your network.',
      totalAlerts: 'Total Alerts',
      highRisk: 'High Risk',
      affectedUsers: 'Affected Users',
      avgRiskScore: 'Avg Risk Score',
      recentAlerts: 'Recent Alerts',
      syncing: 'Syncing...',
      liveStatus: 'Live',
      
      time: 'Time',
      user: 'User',
      domain: 'Domain',
      category: 'Category',
      risk: 'Risk',
      status: 'Status',
      action: 'Action',
      
      statusNew: 'New',
      statusInvestigating: 'investigating',
      statusResolved: 'resolved',
      
      riskHigh: 'High',
      riskMedium: 'Medium',
      riskLow: 'Low',
      
      aiAnalysis: 'AI Analysis',
      alertMetadata: 'Alert Metadata',
      riskScore: 'Risk Score',
      timestamp: 'Timestamp',
      rawLog: 'Raw Log',
      markInvestigating: 'Mark as Investigating',
      resolve: 'Resolve',
      
      loadingAlerts: 'Loading alerts...',
      failedToLoad: 'Failed to load alerts',
      failedToLoadDesc: 'There was a problem fetching alerts. Please try again.',
      allClear: 'All clear!',
      allClearDesc: 'No security alerts detected. Run a simulation to test the system.',
      justNow: 'Just now',
      minsAgo: 'm ago',
      hoursAgo: 'h ago',
      daysAgo: 'd ago',
    },
    login: {
      secureDashboardAccess: 'Secure Dashboard Access',
      signInWithGoogle: 'Sign in with Google',
      connectingToGoogle: 'Connecting to Google...',
    },
    simulation: {
      defenseGridConsole: 'Defense Grid Console',
      simulateShadowAI: 'Simulate Shadow AI',
      simulateDataLeak: 'Simulate Data Leak',
      simulateSafeTraffic: 'Simulate Safe Traffic',
      testSlackAlert: 'Test Slack Alert',
      viewDashboardBtn: 'View Dashboard',
      viewDocumentation: 'View Documentation',
      
      readyToRun: '$ Ready to run simulation. Select an attack vector above...',
      initializingSimulation: '> Initializing simulation...',
      injectingPayload: '> Injecting {type} payload...',
      workerReceived: '> Worker received log entry...',
      runningAnalysis: '> Running analysis...',
      simulationSent: '> Simulation sent: {scenario}',
      expectedRisk: '> Expected risk: {risk}',
      checkDashboard: '> Check dashboard for results',
      clearedPreviousAlerts: '> Cleared previous alerts for fresh simulation...',
      simulationStarted: '> Simulation started successfully',
      simulationInitiated: '> Simulation initiated (backend may still be processing)',
      
      shadowAI: 'Shadow AI',
      dataLeakBlacklist: 'Data Leak (Blacklist)',
      safeTrafficWhitelist: 'Safe Traffic (Whitelist)',
      
      simulationSentOpening: 'Simulation sent. Opening dashboard...',
      slackAlertSent: 'Slack Alert Sent! Security team notified.',
    },
    filterPanel: {
      filterOptions: 'Filter Options',
      riskLevel: 'Risk Level',
      timeRange: 'Time Range',
      eventCategory: 'Event Category',
      applyFilters: 'Apply Filters',
      
      highRisk: 'High Risk (>75)',
      mediumRisk: 'Medium Risk (40-75)',
      lowRisk: 'Low Risk (<40)',
      
      lastHour: 'Last Hour',
      last24Hours: 'Last 24 Hours',
      last7Days: 'Last 7 Days',
      last30Days: 'Last 30 Days',
      allTime: 'All Time',
      
      normalEvents: 'Normal Events',
      shadowIT: 'Shadow IT',
      blacklistedServices: 'Blacklisted Services',
    },
    languageToggle: {
      english: 'EN',
      japanese: '日本語',
      switchLanguage: 'Switch Language',
    },
  },
  
  ja: {
    common: {
      shadowGuard: 'ShadowGuard',
      login: 'ログイン',
      logout: 'ログアウト',
      loading: '読み込み中...',
      error: 'エラー',
      success: '成功',
      view: '表示',
      close: '閉じる',
      apply: '適用',
      clearAll: 'すべてクリア',
      filter: 'フィルター',
      filters: 'フィルター',
      filterActive: 'フィルター有効',
      filtersActive: 'フィルター有効',
    },
    landing: {
      heroTitle: 'シャドーITを検出',
      heroSubtitle: '企業ネットワーク内の未承認SaaS利用、シャドーAI、ファイル共有をリアルタイムで検出します。',
      launchSimulation: 'シミュレーション開始',
      viewDashboard: 'ダッシュボードを見る',
      
      theProblem: '問題点',
      problemTitle: '新しいAIワークフローは',
      problemTitleHighlight: '新たな脅威を意味する',
      problemSubtitle: 'AIサプライチェーンの危殆化。従業員は未承認のAIツールやシャドーSaaSアプリケーションを通じて、知らず知らずのうちに機密データを漏洩しています。',
      
      dataLogAnalysis: 'データログ分析',
      logsProcessed: 'ログ処理済み：',
      realTimeDataStream: 'リアルタイムデータストリーム稼働中',
      threats: '脅威',
      aiScans: 'AIスキャン',
      users: 'ユーザー',
      saasApps: 'SaaSアプリ',
      live: 'ライブ',
      
      threat1Title: '未管理のシャドーAI使用',
      threat1Desc: '従業員が未承認の公開LLMに機密コードや個人情報を貼り付けています。',
      threat2Title: '不正なデータ持ち出し',
      threat2Desc: 'Megaなどのファイル共有サービスへの企業IPの密かなアップロード。',
      threat3Title: 'レガシーファイアウォールの迂回',
      threat3Desc: '暗号化されたSaaSトラフィックは従来の検査ツールを回避することが多い。',
      threat4Title: 'セマンティック可視性の欠如',
      threat4Desc: 'セキュリティチームは、ユーザーがサイトにアクセスした理由のコンテキストを把握できません。',
      
      solutionTitle: '完全な可視化：',
      solutionTitleHighlight: 'シャドーAI',
      solutionSubtitle: 'データがネットワークから出る前に、未承認のGenAI使用を検出、分析、ブロックします。',
      
      solution1Title: 'リアルタイム傍受',
      solution1Desc: 'コレクターエンジンは任意のソース（Zscaler、ファイアウォール）からログを即座に取り込みます',
      solution1Note: 'AIワークフローに入力されるデータ',
      solution2Title: 'AI駆動分析',
      solution2Desc: 'OpenRouter LLMセマンティック分析は、キーワードだけでなくコンテキストを理解します',
      solution2Note: '実行されるコードとその実行場所',
      solution3Title: '即時対応',
      solution3Desc: '自動Slackアラートとダッシュボード可視化をミリ秒単位で実現',
      solution3Note: '出力は本物で安全です',
      
      testDefenseGrid: 'テスト：',
      defenseGridHighlight: '防御グリッド',
      simulationSubtitle: '今すぐAIエンジンに対してライブシミュレーションを実行します。',
      
      systemArchitecture: 'システム',
      architectureHighlight: 'アーキテクチャ',
      logs: 'ログ',
      collector: 'コレクター',
      redis: 'Redis',
      worker: 'ワーカー',
      dashboard: 'ダッシュボード',
      
      githubRepo: 'GitHubリポジトリ',
      apiDocs: 'APIドキュメント',
      teamCredits: 'チームクレジット',
      footerCopyright: '© 2025 ShadowGuard. エージェンティックAI時代のセキュリティを守る。',
    },
    dashboard: {
      securityOverview: 'セキュリティ概要',
      securityOverviewSubtitle: 'ネットワーク内のシャドーIT活動をリアルタイムで監視。',
      totalAlerts: '合計アラート',
      highRisk: '高リスク',
      affectedUsers: '影響ユーザー',
      avgRiskScore: '平均リスクスコア',
      recentAlerts: '最近のアラート',
      syncing: '同期中...',
      liveStatus: 'ライブ',
      
      time: '時間',
      user: 'ユーザー',
      domain: 'ドメイン',
      category: 'カテゴリ',
      risk: 'リスク',
      status: 'ステータス',
      action: 'アクション',
      
      statusNew: '新規',
      statusInvestigating: '調査中',
      statusResolved: '解決済み',
      
      riskHigh: '高',
      riskMedium: '中',
      riskLow: '低',
      
      aiAnalysis: 'AI分析',
      alertMetadata: 'アラートメタデータ',
      riskScore: 'リスクスコア',
      timestamp: 'タイムスタンプ',
      rawLog: '生ログ',
      markInvestigating: '調査中としてマーク',
      resolve: '解決',
      
      loadingAlerts: 'アラートを読み込み中...',
      failedToLoad: 'アラートの読み込みに失敗しました',
      failedToLoadDesc: 'アラートの取得中に問題が発生しました。もう一度お試しください。',
      allClear: '問題なし！',
      allClearDesc: 'セキュリティアラートは検出されませんでした。システムをテストするにはシミュレーションを実行してください。',
      justNow: 'たった今',
      minsAgo: '分前',
      hoursAgo: '時間前',
      daysAgo: '日前',
    },
    login: {
      secureDashboardAccess: '安全なダッシュボードアクセス',
      signInWithGoogle: 'Googleでサインイン',
      connectingToGoogle: 'Googleに接続中...',
    },
    simulation: {
      defenseGridConsole: '防御グリッドコンソール',
      simulateShadowAI: 'シャドーAIをシミュレート',
      simulateDataLeak: 'データ漏洩をシミュレート',
      simulateSafeTraffic: '安全なトラフィックをシミュレート',
      testSlackAlert: 'Slackアラートをテスト',
      viewDashboardBtn: 'ダッシュボードを見る',
      viewDocumentation: 'ドキュメントを見る',
      
      readyToRun: '$ シミュレーション実行準備完了。上記から攻撃ベクトルを選択してください...',
      initializingSimulation: '> シミュレーションを初期化中...',
      injectingPayload: '> {type}ペイロードを注入中...',
      workerReceived: '> ワーカーがログエントリを受信...',
      runningAnalysis: '> 分析を実行中...',
      simulationSent: '> シミュレーション送信完了：{scenario}',
      expectedRisk: '> 予想リスク：{risk}',
      checkDashboard: '> ダッシュボードで結果を確認してください',
      clearedPreviousAlerts: '> 新規シミュレーションのため以前のアラートをクリア...',
      simulationStarted: '> シミュレーションが正常に開始されました',
      simulationInitiated: '> シミュレーションが開始されました（バックエンドがまだ処理中の可能性があります）',
      
      shadowAI: 'シャドーAI',
      dataLeakBlacklist: 'データ漏洩（ブラックリスト）',
      safeTrafficWhitelist: '安全なトラフィック（ホワイトリスト）',
      
      simulationSentOpening: 'シミュレーション送信完了。ダッシュボードを開いています...',
      slackAlertSent: 'Slackアラート送信完了！セキュリティチームに通知しました。',
    },
    filterPanel: {
      filterOptions: 'フィルターオプション',
      riskLevel: 'リスクレベル',
      timeRange: '時間範囲',
      eventCategory: 'イベントカテゴリ',
      applyFilters: 'フィルターを適用',
      
      highRisk: '高リスク（>75）',
      mediumRisk: '中リスク（40-75）',
      lowRisk: '低リスク（<40）',
      
      lastHour: '過去1時間',
      last24Hours: '過去24時間',
      last7Days: '過去7日間',
      last30Days: '過去30日間',
      allTime: '全期間',
      
      normalEvents: '通常イベント',
      shadowIT: 'シャドーIT',
      blacklistedServices: 'ブラックリストサービス',
    },
    languageToggle: {
      english: 'EN',
      japanese: '日本語',
      switchLanguage: '言語を切り替え',
    },
  },
};
