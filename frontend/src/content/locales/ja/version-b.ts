import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionB: VersionContent = {
  meta: {
    title: 'Claude、ChatGPT、Cursor向けAI長期記憶 | Interview Assistant MCP',
    description:
      'あらゆるAIアシスタントに構造化された長期記憶を提供。アクティブなインタビューで深い知識を抽出。MCPサーバーはClaude Desktop、ChatGPT、Cursorなどと連携。',
    ogImage: '/og-image-dev.png',
    canonicalPath: '/developers',
  },

  hero: {
    headline: 'どんなAIアシスタントにも構造化された長期記憶を',
    subheadline:
      'ただの受動的な記憶保存ではありません。アクティブなインタビューで深く構造化された知識を抽出。あなたのAIが本当に文脈を理解します。',
    cta: '早期アクセスに参加する',
    socialProof: 'Claude、ChatGPT、Cursor、Windsurfなどに対応',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: 'AIの記憶は受動的であってはならない',
    items: [
      {
        title: '浅い記録',
        description:
          'Mem0のようなツールは断片を受動的に記録します。「ユーザーはPythonが好き」という情報は得られますが、「50万行のJavaコードベースをPythonに移行し、デプロイ時間を60％短縮した」という深い知識は得られません。',
        icon: 'layers',
      },
      {
        title: '構造がない',
        description:
          'ナレッジグラフはエンティティや関係性を捉えますが、物語性が欠けています。文脈にストーリーがなければ、ただのノイズです。',
        icon: 'grid',
      },
      {
        title: '繰り返し説明する',
        description:
          'Claudeとの会話は毎回ゼロから始まります。同じ背景情報を何度もコピー＆ペーストしなければなりません。毎回です。',
        icon: 'repeat',
      },
    ],
  },

  whyNotChatGPT: {
    heading: 'アクティブなインタビュー > 受動的な記録',
    description:
      '他の記憶ツールはあなたの行動を見て断片を受動的に保存します。\n\n私たちはあなたにインタビューします。体系的に。ジャーナリストがプロフィールを作るように—フォローアップを行い、深掘りし、何がカバーされ何がされていないかを追跡します。\n\n結果は、AIが単に検索するだけでなく実際に活用できる、構造化され包括的な知識です。',
    before: {
      label: 'Mem0が保存するのは',
      text: 'ユーザーはPythonを知っている',
    },
    after: {
      label: '私たちが保存するのは',
      text: 'Acme社でのPython移行を主導（2023年）。50万行のJavaモノリスをPythonマイクロサービスに変換。8人チーム。デプロイ時間を60％削減。非同期処理にはDjangoではなくFastAPIを選択。',
    },
    closing: 'これが記憶と理解の違いです。',
  },

  howItWorks: {
    heading: '仕組み',
    steps: [
      {
        number: 1,
        title: '構造化インタビュー',
        description:
          'Telegramでの短い会話で体系的に知識をカバー。AIが質問済みの内容と未質問の内容を把握。断片的ではなく段階的に深掘りします。',
      },
      {
        number: 2,
        title: '知識抽出',
        description:
          'AIが意味的埋め込みを使って構造化された要約を抽出。生活領域ごとに整理され、キーワードだけでなく意味で検索可能。',
      },
      {
        number: 3,
        title: 'MCP連携',
        description:
          'Claude Desktop、ChatGPT、Cursor、Windsurf、VS Codeなど、あらゆるMCP対応AIと連携する標準MCPサーバー。Bearerトークン認証。5分でセットアップ完了。',
      },
    ],
    bonus: {
      title: '近日公開予定：MCPアプリ',
      description:
        'ClaudeやChatGPT内で直接表示されるインタラクティブな知識ダッシュボードを新しいMCPアプリ拡張機能で提供予定。',
    },
  },

  benefits: {
    columns: [
      {
        title: '開発者向け',
        items: [
          '技術スタック、アーキテクチャの決定、コーディングパターンをAIが記憶',
          '過去のプロジェクトをどんな会話でも参照可能',
          'あなたの実際のパターンを使ったコード例を生成',
          'コードベースのセットアップを繰り返し説明する必要なし',
        ],
      },
      {
        title: 'コンサルタント向け',
        items: [
          'クライアント情報、手法、過去の案件をAIが記憶',
          '実績に基づく提案書を作成',
          '背景情報を繰り返す必要なし',
          '過去の会話を自動的に活用',
        ],
      },
      {
        title: 'すべての人に',
        items: [
          '実績に基づいたカバーレター作成',
          'あなたのストーリーを知るAIと面接準備',
          '知識から自動生成されるプロフェッショナルな履歴書',
          'データはいつでもエクスポート可能',
        ],
      },
    ],
  },

  pricing: {
    heading: 'シンプルな料金体系。驚きなし。',
    tiers: [
      {
        name: '無料',
        price: null,
        priceLabel: '無料',
        description: 'インタビュー1回＋知識検索デモ。',
        features: ['インタビュー1回', '知識検索デモ'],
        cta: '無料で試す',
        highlighted: false,
      },
      {
        name: 'Knowledge Pro',
        price: 29,
        priceLabel: '$29/月',
        description: 'インタビュー、MCPサーバー、履歴書生成のフルアクセス。',
        features: [
          '無制限のインタビューと知識抽出',
          'MCPサーバーアクセス（Bearerトークン認証）',
          '全知識に対する意味検索',
          '履歴書生成機能付き',
          'Claude、ChatGPT、Cursor、Windsurf対応',
        ],
        cta: '早期アクセスに参加',
        highlighted: true,
        badge: '人気No.1',
      },
      {
        name: 'セルフホスト',
        price: 59,
        priceLabel: '$59/月',
        description: 'Knowledge Proの全機能を自社インフラで利用可能。',
        features: [
          'Knowledge Proの全機能',
          'Docker展開、ソースコード完全アクセス',
          'データ完全所有権',
          '優先サポート',
        ],
        cta: '早期アクセスに参加',
        highlighted: false,
      },
    ],
  },

  faq: {
    items: [
      {
        question: 'Mem0/OpenMemoryと何が違うの？',
        answer:
          'Mem0はAIとの会話から断片を受動的に記録します。私たちは体系的にカバー範囲を追跡しながらアクティブにインタビューし、深く構造化された知識を抽出します。防犯カメラとジャーナリストのインタビューの違いです。',
      },
      {
        question: 'Zepとは何が違うの？',
        answer:
          'Zepはドキュメントや会話からナレッジグラフを作成します。私たちはフォローアップ質問と段階的な深掘りを伴う構造化インタビューを行います。意図的に抽出された知識なので、より豊かです。',
      },
      {
        question: '対応しているAIは？',
        answer:
          'MCP対応のAIすべて。確認済みはClaude Desktop、ChatGPT、Cursor、Windsurf、VS Code Copilot、JetBrains、Goose、Raycast。MCPは現在業界標準（Linux Foundation）です。',
      },
      {
        question: 'MCPプロトコルは安定している？',
        answer:
          'MCPはAgentic AI Foundation（Linux Foundation）が管理し、Anthropic、OpenAI、Google、Microsoft、AWSがメンバーです。後方互換性を維持しています。',
      },
      {
        question: 'セルフホストは可能？',
        answer:
          'はい。セルフホストプランにはDocker Composeセットアップと完全な展開ドキュメントが含まれます。',
      },
      {
        question: 'データはエクスポートできる？',
        answer:
          'いつでも可能です。JSONやPDF形式でデータをダウンロードできます。あなたのものです。',
      },
      {
        question: '支払い方法は？',
        answer:
          'クレジットカード、Apple Pay、Google Payを決済パートナー経由で利用可能。プライバシー重視の方にはUSDCやBTCも対応しています。',
      },
    ],
  },

  emailSignup: {
    heading: '早期アクセスを獲得',
    subheading: '構造化されたAI記憶をいち早く体験。',
    placeholder: 'メールアドレスを入力',
    cta: '早期アクセスに無料で参加',
    disclaimer:
      'スパムなし。クレジットカード不要。リリース時にお知らせします。',
    formAction: formspree.action,
  },
};
