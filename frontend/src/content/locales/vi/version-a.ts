import { formspree } from '../../constants';
import type { VersionContent } from '../../types';

export const versionA: VersionContent = {
  meta: {
    title:
      'Huấn luyện viên nghề nghiệp AI - CV chuyên nghiệp trong 15 phút | Interview Assistant',
    description:
      'Nói chuyện tự nhiên, nhận CV chuyên nghiệp tối ưu ATS. AI phỏng vấn bạn như huấn luyện viên nghề nghiệp, khai thác thành tích, tạo CV hoàn chỉnh. Miễn phí.',
    ogImage: '/og-image-cv.png',
    canonicalPath: '/',
  },

  hero: {
    headline:
      'Huấn luyện viên nghề nghiệp AI của bạn.<br>CV hoàn hảo trong 15 phút.',
    subheadline:
      'Nói chuyện tự nhiên về kinh nghiệm của bạn. AI phỏng vấn bạn như huấn luyện viên nghề nghiệp, khai thác thành tích và tự động tạo CV chuyên nghiệp tối ưu ATS.',
    cta: 'Dùng thử miễn phí',
    socialProof: 'Tham gia cùng hơn 50 chuyên gia trong danh sách chờ',
    heroImage: '/hero-mockup.png',
    videoId: 'dQw4w9WgXcQ', // placeholder — replace with real demo
  },

  problem: {
    heading: 'Có quen thuộc không?',
    items: [
      {
        title: 'Bạn quên mất những thành tựu tốt nhất',
        description:
          '"Tôi đã đạt được gì ở công việc đó 3 năm trước?" Bạn đã làm những điều tuyệt vời nhưng không thể diễn đạt khi bị áp lực.',
        icon: 'brain',
      },
      {
        title: 'ChatGPT cho bạn nội dung chung chung',
        description:
          'Bạn dán thông tin, ChatGPT viết "chuyên gia hướng kết quả với thành tích đã được chứng minh." Nhà tuyển dụng nhận ra ngay.',
        icon: 'sparkles',
      },
      {
        title: 'Cập nhật mất hàng giờ',
        description:
          'Mỗi lần ứng tuyển là phải định dạng lại, viết lại và hy vọng ATS không từ chối bạn. Bạn còn nhiều việc quan trọng hơn.',
        icon: 'clock',
      },
    ],
  },

  whyNotChatGPT: {
    heading: 'ChatGPT Viết CV.<br>Chúng tôi Viết CV CỦA BẠN.',
    description:
      'ChatGPT có thể chỉnh sửa văn bản bạn cung cấp. Nhưng hầu hết mọi người không thể diễn đạt thành tích của mình rõ ràng.\n\nAI của chúng tôi phỏng vấn bạn như huấn luyện viên nghề nghiệp — hỏi thêm, khai thác tác động định lượng, bắt những điều bạn dễ quên.',
    before: {
      label: 'Nội dung chung của ChatGPT',
      text: 'Quản lý một nhóm phát triển',
    },
    after: {
      label: 'Nội dung khai thác qua phỏng vấn',
      text: 'Dẫn dắt đội kỹ sư 12 người hoàn thành di chuyển nền tảng trị giá $2M trước 3 tuần so với kế hoạch',
    },
    closing: 'Bạn đã biết những điều này. Bạn chỉ cần ai đó hỏi đúng câu hỏi.',
  },

  howItWorks: {
    heading: '15 Phút. Chỉ vậy thôi.',
    steps: [
      {
        number: 1,
        title: 'Trò chuyện nhanh',
        description:
          'Chat với bot Telegram của chúng tôi trong 10-15 phút. Nói chuyện tự nhiên về kinh nghiệm, dự án, kỹ năng. Bot hỏi thêm thông minh — như huấn luyện viên nghề nghiệp, không phải mẫu đơn.',
      },
      {
        number: 2,
        title: 'AI khai thác',
        description:
          'AI của chúng tôi khai thác thành tích, định lượng tác động, nhận diện kỹ năng chính và tổ chức mọi thứ thành dữ liệu nghề nghiệp có cấu trúc. Không bỏ sót gì.',
      },
      {
        number: 3,
        title: 'CV chuyên nghiệp',
        description:
          'Nhận CV PDF bóng bẩy, tối ưu ATS. Định dạng chuẩn, nhiều từ khóa, vượt qua sàng lọc tự động. Sẵn sàng cho mọi đơn ứng tuyển.',
      },
    ],
    bonus: {
      title: 'Quà tặng: Bộ nhớ AI',
      description:
        'Trợ lý AI của bạn (Claude, ChatGPT, Cursor) giờ có thể truy vấn lịch sử nghề nghiệp bất cứ lúc nào. Viết thư xin việc trong vài giây. Chuẩn bị phỏng vấn với kinh nghiệm thực tế của bạn.',
    },
  },

  benefits: {
    columns: [
      {
        title: 'Như một huấn luyện viên nghề nghiệp',
        items: [
          'Phỏng vấn hướng dẫn khai thác thành tích tốt nhất của bạn',
          'Câu hỏi tiếp theo bạn không nghĩ đến tự hỏi bản thân',
          'Tự động ghi nhận thành tích định lượng',
          'Cập nhật trong các buổi theo dõi 5 phút',
        ],
      },
      {
        title: 'Tối ưu ATS',
        items: [
          'Vượt qua sàng lọc tự động (75% CV không vượt được)',
          'Nội dung nhiều từ khóa phù hợp ngành nghề',
          'Định dạng sạch sẽ giúp hệ thống ATS đọc được',
          'Bố cục chuyên nghiệp nhà tuyển dụng mong đợi',
        ],
      },
      {
        title: 'Luôn cập nhật',
        items: [
          'Thêm kinh nghiệm mới bất cứ lúc nào qua chat nhanh',
          'Tạo các phiên bản CV phù hợp từng vị trí',
          'Xuất PDF ngay lập tức',
          'Dữ liệu của bạn, bạn kiểm soát, xuất bất cứ lúc nào',
        ],
      },
    ],
  },

  pricing: {
    heading: 'Giá cả đơn giản. Không bất ngờ.',
    tiers: [
      {
        name: 'Miễn phí',
        price: null,
        priceLabel: 'Miễn phí',
        description:
          'Thử xem có phù hợp với bạn không. Không cần thẻ tín dụng.',
        features: ['1 buổi phỏng vấn', '1 lần tạo CV'],
        cta: 'Dùng thử miễn phí',
        highlighted: false,
      },
      {
        name: 'CV Pro — Trọn đời',
        price: 79,
        priceLabel: '$79 một lần',
        description:
          'Thanh toán một lần, dùng mãi mãi. Giá dành cho thành viên sáng lập.',
        features: [
          'Phỏng vấn và tạo CV không giới hạn',
          'Xuất PDF tối ưu ATS',
          'Nhiều phiên bản CV',
          'Truy cập bot Telegram',
        ],
        cta: 'Đặt trước quyền truy cập trọn đời',
        highlighted: true,
        badge: 'Giá trị tốt nhất',
      },
    ],
  },

  faq: {
    items: [
      {
        question: 'Điểm khác biệt so với ChatGPT là gì?',
        answer:
          'ChatGPT chỉnh sửa văn bản bạn có sẵn. Chúng tôi phỏng vấn bạn — hỏi thêm, khai thác chi tiết, ghi nhận thành tích bạn dễ quên. Giống huấn luyện viên nghề nghiệp hơn là trình soạn thảo văn bản. Kết quả phong phú, cụ thể và độc đáo cho bạn.',
      },
      {
        question: 'CV có thân thiện với ATS không?',
        answer:
          'Có. Định dạng sạch, cấu trúc tiêu đề chuẩn, nội dung nhiều từ khóa. Thiết kế để vượt qua hệ thống sàng lọc tự động từ chối 75% CV.',
      },
      {
        question: 'Tôi có cần kỹ năng kỹ thuật không?',
        answer:
          'Không. Nếu bạn dùng được Telegram, bạn dùng được. Chỉ cần chat tự nhiên. Tính năng trợ lý AI (bộ nhớ Claude/ChatGPT) là phần thưởng cho người dùng kỹ thuật.',
      },
      {
        question: 'Gói miễn phí hoạt động thế nào?',
        answer:
          'Một buổi phỏng vấn đầy đủ và một lần tạo CV hoàn toàn miễn phí. Không cần thẻ tín dụng. Nếu thích, bạn có thể nâng cấp để tiếp tục tạo và cập nhật.',
      },
      {
        question: 'Tôi có thể xuất dữ liệu không?',
        answer:
          'Luôn luôn. Tải dữ liệu của bạn dưới dạng JSON/PDF bất cứ lúc nào. Dữ liệu thuộc về bạn.',
      },
      {
        question: 'Phương thức thanh toán nào được chấp nhận?',
        answer:
          'Thẻ tín dụng, Apple Pay, Google Pay qua đối tác thanh toán của chúng tôi. Chúng tôi cũng chấp nhận USDC và BTC cho khách hàng quan tâm đến quyền riêng tư.',
      },
      {
        question: 'Nếu tôi không hài lòng thì sao?',
        answer:
          'Hủy bất cứ lúc nào. Gói tháng không ràng buộc. Mua trọn đời có bảo đảm hoàn tiền trong 30 ngày.',
      },
    ],
  },

  emailSignup: {
    heading: 'Nhận quyền truy cập sớm',
    subheading:
      'Gói miễn phí có sẵn khi ra mắt. Hãy là người đầu tiên trải nghiệm.',
    placeholder: 'Nhập email của bạn',
    cta: 'Tham gia danh sách chờ — Miễn phí',
    disclaimer: 'Không spam. Không cần thẻ tín dụng. Chỉ thông báo khi ra mắt.',
    formAction: formspree.action,
  },
};
