import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionB: VersionContent = {
  meta: {
    title:
      'Bộ Nhớ Dài Hạn AI cho Claude, ChatGPT & Cursor | Interview Assistant MCP',
    description:
      'Trang bị bộ nhớ dài hạn có cấu trúc cho bất kỳ trợ lý AI nào. Các cuộc phỏng vấn chủ động khai thác kiến thức sâu sắc. Máy chủ MCP hoạt động với Claude Desktop, ChatGPT, Cursor và nhiều hơn nữa.',
    ogImage: '/og-image-dev.png',
    canonicalPath: '/developers',
  },

  hero: {
    headline: 'Trang Bị Bộ Nhớ Dài Hạn Có Cấu Trúc Cho BẤT KỲ Trợ Lý AI Nào',
    subheadline:
      'Không phải là một kho lưu trữ thụ động. Các cuộc phỏng vấn chủ động khai thác kiến thức sâu sắc, có cấu trúc. AI của bạn thực sự hiểu bối cảnh của bạn.',
    cta: 'Tham Gia Truy Cập Sớm',
    socialProof:
      'Tương thích với Claude, ChatGPT, Cursor, Windsurf & nhiều hơn nữa',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: 'Bộ Nhớ AI Không Nên Chỉ Là Thụ Động',
    items: [
      {
        title: 'Ghi nhận nông cạn',
        description:
          'Các công cụ như Mem0 chỉ ghi lại các mảnh rời rạc một cách thụ động. Bạn nhận được "người dùng thích Python" chứ không phải "dẫn dắt di cư 500K LOC codebase Java sang Python, giảm thời gian triển khai 60%."',
        icon: 'layers',
      },
      {
        title: 'Không có cấu trúc',
        description:
          'Đồ thị kiến thức ghi nhận thực thể và mối quan hệ nhưng thiếu câu chuyện. Bối cảnh không có câu chuyện chỉ là tiếng ồn.',
        icon: 'grid',
      },
      {
        title: 'Bạn phải lặp lại chính mình',
        description:
          'Mỗi cuộc trò chuyện với Claude bắt đầu từ con số không. Sao chép-dán cùng một bối cảnh. Mỗi. Lần. Một cách liên tục.',
        icon: 'repeat',
      },
    ],
  },

  whyNotChatGPT: {
    heading: 'Phỏng Vấn Chủ Động > Ghi Nhận Thụ Động',
    description:
      'Các công cụ bộ nhớ khác chỉ theo dõi hành động của bạn và lưu trữ các mảnh một cách thụ động.\n\nChúng tôi phỏng vấn bạn. Có hệ thống. Giống như một nhà báo xây dựng hồ sơ — hỏi thêm, đào sâu hơn, theo dõi những gì đã đề cập và chưa đề cập.\n\nKết quả: kiến thức có cấu trúc, toàn diện mà AI thực sự có thể SỬ DỤNG, không chỉ truy xuất.',
    before: {
      label: 'Mem0 lưu trữ',
      text: 'người dùng biết Python',
    },
    after: {
      label: 'Chúng tôi lưu trữ',
      text: 'Dẫn dắt di cư Python tại Acme Corp (2023). Chuyển đổi 500K LOC Java monolith sang microservices Python. Đội ngũ 8 người. Giảm thời gian triển khai 60%. Chọn FastAPI thay vì Django cho khối lượng công việc bất đồng bộ.',
    },
    closing: 'Đó là sự khác biệt giữa bộ nhớ và sự thấu hiểu.',
  },

  howItWorks: {
    heading: 'Cách Thức Hoạt Động',
    steps: [
      {
        number: 1,
        title: 'Phỏng Vấn Có Cấu Trúc',
        description:
          'Các cuộc trò chuyện nhanh trên Telegram bao quát kiến thức của bạn một cách hệ thống. AI theo dõi phạm vi — biết những gì đã hỏi và chưa hỏi. Đào sâu tiến triển, không phải các mảnh rời rạc ngẫu nhiên.',
      },
      {
        number: 2,
        title: 'Khai Thác Kiến Thức',
        description:
          'AI trích xuất các bản tóm tắt có cấu trúc với nhúng ngữ nghĩa. Tổ chức theo lĩnh vực cuộc sống, tìm kiếm theo ý nghĩa, không chỉ từ khóa.',
      },
      {
        number: 3,
        title: 'Tích Hợp MCP',
        description:
          'Máy chủ MCP tiêu chuẩn hoạt động với Claude Desktop, ChatGPT, Cursor, Windsurf, VS Code và bất kỳ AI tương thích MCP nào. Xác thực Bearer token. Cài đặt trong 5 phút.',
      },
    ],
    bonus: {
      title: 'Sắp Ra Mắt: Ứng Dụng MCP',
      description:
        'Bảng điều khiển kiến thức tương tác được hiển thị trực tiếp trong Claude và ChatGPT qua tiện ích mở rộng MCP Apps mới.',
    },
  },

  benefits: {
    columns: [
      {
        title: 'Dành Cho Nhà Phát Triển',
        items: [
          'AI ghi nhớ ngăn xếp công nghệ, quyết định kiến trúc và mẫu mã lập trình của bạn',
          'Tham chiếu dự án trước trong mọi cuộc trò chuyện',
          'Tạo ví dụ mã theo mẫu thực tế của BẠN',
          'Không bao giờ phải giải thích lại cách thiết lập codebase',
        ],
      },
      {
        title: 'Dành Cho Tư Vấn Viên',
        items: [
          'AI ghi nhớ chi tiết khách hàng, phương pháp luận, các dự án trước',
          'Viết đề xuất dựa trên kinh nghiệm thực tế',
          'Không bao giờ phải lặp lại thông tin nền nữa',
          'Tự động xây dựng dựa trên các cuộc trò chuyện trước',
        ],
      },
      {
        title: 'Dành Cho Mọi Người',
        items: [
          'Thư xin việc được viết dựa trên thành tích thực tế',
          'Chuẩn bị phỏng vấn với AI hiểu câu chuyện của bạn',
          'Tự động tạo CV chuyên nghiệp từ kiến thức của bạn',
          'Dữ liệu của bạn, luôn có thể xuất ra',
        ],
      },
    ],
  },

  pricing: {
    heading: 'Giá Cả Đơn Giản. Không Bất Ngờ.',
    tiers: [
      {
        name: 'Miễn Phí',
        price: null,
        priceLabel: 'Miễn Phí',
        description: '1 phiên phỏng vấn + demo tìm kiếm kiến thức.',
        features: ['1 phiên phỏng vấn', 'Demo tìm kiếm kiến thức'],
        cta: 'Dùng Thử Miễn Phí',
        highlighted: false,
      },
      {
        name: 'Knowledge Pro',
        price: 29,
        priceLabel: '$29/tháng',
        description: 'Truy cập đầy đủ phỏng vấn, máy chủ MCP và tạo CV.',
        features: [
          'Phỏng vấn không giới hạn + khai thác kiến thức',
          'Truy cập máy chủ MCP (xác thực Bearer token)',
          'Tìm kiếm ngữ nghĩa trên toàn bộ kiến thức của bạn',
          'Bao gồm tạo CV',
          'Tương thích với Claude, ChatGPT, Cursor, Windsurf',
        ],
        cta: 'Tham Gia Truy Cập Sớm',
        highlighted: true,
        badge: 'Phổ Biến Nhất',
      },
      {
        name: 'Tự Lưu Trữ',
        price: 59,
        priceLabel: '$59/tháng',
        description: 'Tất cả trong Knowledge Pro, trên hạ tầng của bạn.',
        features: [
          'Tất cả trong Knowledge Pro',
          'Triển khai Docker, truy cập mã nguồn đầy đủ',
          'Quyền sở hữu dữ liệu toàn diện',
          'Hỗ trợ ưu tiên',
        ],
        cta: 'Tham Gia Truy Cập Sớm',
        highlighted: false,
      },
    ],
  },

  faq: {
    items: [
      {
        question: 'Điểm khác biệt so với Mem0/OpenMemory là gì?',
        answer:
          'Mem0 ghi nhận các mảnh rời rạc từ các cuộc trò chuyện AI của bạn một cách thụ động. Chúng tôi phỏng vấn bạn một cách chủ động — có hệ thống, theo dõi phạm vi — khai thác kiến thức sâu sắc có cấu trúc. Đó là sự khác biệt giữa camera an ninh và phỏng vấn nhà báo.',
      },
      {
        question: 'Điểm khác biệt so với Zep là gì?',
        answer:
          'Zep xây dựng đồ thị kiến thức từ tài liệu và cuộc trò chuyện. Chúng tôi thực hiện phỏng vấn có cấu trúc chủ động với các câu hỏi tiếp theo và đào sâu dần. Kiến thức của chúng tôi phong phú hơn vì được khai thác có chủ ý, không chỉ quan sát thụ động.',
      },
      {
        question: 'Những AI nào được hỗ trợ?',
        answer:
          'Bất kỳ AI tương thích MCP nào. Xác nhận: Claude Desktop, ChatGPT, Cursor, Windsurf, VS Code Copilot, JetBrains, Goose, Raycast. MCP hiện là tiêu chuẩn ngành (Linux Foundation).',
      },
      {
        question: 'Giao thức MCP có ổn định không?',
        answer:
          'MCP được quản lý bởi Agentic AI Foundation (Linux Foundation) với sự tham gia của Anthropic, OpenAI, Google, Microsoft và AWS. Chúng tôi duy trì tương thích ngược.',
      },
      {
        question: 'Tôi có thể tự lưu trữ không?',
        answer:
          'Có. Gói Tự Lưu Trữ bao gồm thiết lập Docker Compose và tài liệu triển khai đầy đủ.',
      },
      {
        question: 'Tôi có thể xuất dữ liệu của mình không?',
        answer:
          'Luôn luôn. Tải dữ liệu của bạn dưới dạng JSON/PDF bất cứ lúc nào. Dữ liệu thuộc về bạn.',
      },
      {
        question: 'Phương thức thanh toán nào được chấp nhận?',
        answer:
          'Thẻ tín dụng, Apple Pay, Google Pay qua đối tác thanh toán của chúng tôi. Chúng tôi cũng chấp nhận USDC và BTC cho khách hàng quan tâm đến quyền riêng tư.',
      },
    ],
  },

  emailSignup: {
    heading: 'Nhận Truy Cập Sớm',
    subheading: 'Trở thành người đầu tiên trải nghiệm bộ nhớ AI có cấu trúc.',
    placeholder: 'Nhập email của bạn',
    cta: 'Tham Gia Truy Cập Sớm — Miễn Phí',
    disclaimer:
      'Không spam. Không cần thẻ tín dụng. Chỉ là thông báo khi chúng tôi ra mắt.',
    formAction: formspree.action,
  },
};
