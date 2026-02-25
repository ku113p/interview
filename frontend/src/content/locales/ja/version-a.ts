import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionA: VersionContent = {
  meta: {
    title:
      'AIキャリアコーチ - 15分でプロフェッショナルな履歴書作成 | Interview Assistant',
    description:
      '自然に話すだけで、プロ仕様のATS最適化履歴書が完成。AIがキャリアコーチのように面接し、実績を引き出し、洗練された履歴書を自動生成。無料プランあり。',
    ogImage: '/og-image-cv.png',
    canonicalPath: '/',
  },

  hero: {
    headline: 'あなたのAIキャリアコーチ。<br>15分で完璧な履歴書。',
    subheadline:
      '経験を自然に語ってください。AIがキャリアコーチのように面接し、実績を引き出し、ATS最適化されたプロフェッショナルな履歴書を自動で作成します。',
    cta: '無料で試す',
    socialProof: '50人以上のプロが待機リストに参加中',
    heroImage: '/hero-mockup.png',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: 'こんな経験ありませんか？',
    items: [
      {
        title: '最高の仕事を忘れてしまう',
        description:
          '「3年前のあの仕事で何を成し遂げたっけ？」素晴らしい実績があっても、プレッシャーの中でうまく伝えられない。',
        icon: 'brain',
      },
      {
        title: 'ChatGPTはありきたりな文章を出す',
        description:
          '情報を貼り付けると「実績豊富な結果重視のプロフェッショナル」といったありきたりな文章に。採用担当者にはすぐに見抜かれます。',
        icon: 'sparkles',
      },
      {
        title: '更新に何時間もかかる',
        description:
          '応募のたびにフォーマットを直し、書き直し、ATSに弾かれないか祈る。もっと大事なことに時間を使いたいですよね。',
        icon: 'clock',
      },
    ],
  },

  whyNotChatGPT: {
    heading: 'ChatGPTは履歴書を作る。<br>私たちはあなたの履歴書を作る。',
    description:
      'ChatGPTは与えられた文章を磨くことはできますが、多くの人は自分の実績をうまく言葉にできません。\n\n私たちのAIはキャリアコーチのように面接し、フォローアップ質問をし、定量的な成果を引き出し、忘れがちなポイントもキャッチします。',
    before: {
      label: '一般的なChatGPTの出力',
      text: '開発チームを管理した',
    },
    after: {
      label: '面接で引き出した出力',
      text: '12人のエンジニアチームを率い、200万ドル規模のプラットフォーム移行を予定より3週間早く完了させた',
    },
    closing:
      'あなたはもう知っていることです。ただ、正しい質問をしてくれる相手が必要なだけ。',
  },

  howItWorks: {
    heading: '15分。それだけです。',
    steps: [
      {
        number: 1,
        title: '簡単な会話',
        description:
          'Telegramボットと10〜15分チャット。経験やプロジェクト、スキルについて自然に話すだけ。キャリアコーチのように賢いフォローアップ質問をします。',
      },
      {
        number: 2,
        title: 'AIによる抽出',
        description:
          'AIが実績を抽出し、影響を定量化し、重要なスキルを特定。すべてを構造化されたキャリアデータに整理。情報は一切漏れません。',
      },
      {
        number: 3,
        title: 'プロ仕様の履歴書',
        description:
          '洗練されたATS最適化済みPDF履歴書を入手。適切なフォーマット、キーワード豊富で自動審査を通過。どんな応募にも対応可能。',
      },
    ],
    bonus: {
      title: 'ボーナス：AIメモリー',
      description:
        'Claude、ChatGPT、CursorなどのAIアシスタントがあなたのキャリア履歴をいつでも参照可能。数秒でカバーレター作成。実際の経験で面接準備。',
    },
  },

  benefits: {
    columns: [
      {
        title: 'キャリアコーチのように',
        items: [
          'ガイド付き面接で最高の実績を引き出す',
          '自分では思いつかないフォローアップ質問',
          '定量的な成果を自動でキャプチャ',
          '5分のフォローアップで更新可能',
        ],
      },
      {
        title: 'ATS最適化済み',
        items: [
          '自動審査を通過（75%の履歴書は通過しません）',
          '業界にマッチしたキーワード豊富な内容',
          'ATSが解析可能なクリーンなフォーマット',
          '採用担当者が期待するプロ仕様のレイアウト',
        ],
      },
      {
        title: '常に最新',
        items: [
          'チャットでいつでも新しい経験を追加',
          '役割ごとにカスタマイズしたバージョンを生成',
          'PDFを即時エクスポート',
          'あなたのデータはあなたのもの。いつでもエクスポート可能',
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
        description: 'まずは試してみてください。クレジットカード不要。',
        features: ['面接セッション1回', '履歴書生成1回'],
        cta: '無料で試す',
        highlighted: false,
      },
      {
        name: 'CV Pro — 永久ライセンス',
        price: 79,
        priceLabel: '$79 一括払い',
        description: '一度支払えばずっと使えます。創業メンバー価格。',
        features: [
          '面接・履歴書生成無制限',
          'ATS最適化PDFエクスポート',
          '複数の履歴書バージョン',
          'Telegramボットアクセス',
        ],
        cta: '永久アクセスを予約',
        highlighted: true,
        badge: 'ベストバリュー',
      },
    ],
  },

  faq: {
    items: [
      {
        question: 'これはChatGPTとどう違うの？',
        answer:
          'ChatGPTは既存の文章を磨きますが、私たちはあなたに面接し、フォローアップ質問をして具体的な実績を引き出します。キャリアコーチのように寄り添い、より豊かで具体的、そしてあなただけの履歴書を作成します。',
      },
      {
        question: '履歴書はATSに対応していますか？',
        answer:
          'はい。クリーンなフォーマット、適切な見出し階層、キーワード豊富な内容で、75%の履歴書が弾かれる自動審査を通過するよう設計されています。',
      },
      {
        question: '技術的なスキルは必要ですか？',
        answer:
          'いいえ。Telegramが使えればOKです。自然にチャットするだけ。AIアシスタント機能（Claude/ChatGPTメモリー）は技術ユーザー向けのボーナスです。',
      },
      {
        question: '無料プランはどうなっていますか？',
        answer:
          '面接セッション1回と履歴書生成1回が完全無料。クレジットカード不要。気に入ったらアップグレードして継続利用できます。',
      },
      {
        question: 'データはエクスポートできますか？',
        answer:
          'いつでも可能です。JSONやPDF形式でダウンロードできます。あなたのデータはあなたのものです。',
      },
      {
        question: '支払い方法は何がありますか？',
        answer:
          'クレジットカード、Apple Pay、Google Payを決済パートナー経由で対応。プライバシー重視の方にはUSDCやBTCも受け付けています。',
      },
      {
        question: '気に入らなかったらどうすれば？',
        answer:
          'いつでもキャンセル可能。月額プランは縛りなし。永久ライセンスは30日間返金保証付きです。',
      },
    ],
  },

  emailSignup: {
    heading: '早期アクセスを手に入れよう',
    subheading: 'ローンチ時に無料プラン利用可能。いち早く試せます。',
    placeholder: 'メールアドレスを入力',
    cta: '待機リストに参加 — 無料',
    disclaimer:
      'スパムなし。クレジットカード不要。ローンチ時にお知らせします。',
    formAction: formspree.action,
  },
};
