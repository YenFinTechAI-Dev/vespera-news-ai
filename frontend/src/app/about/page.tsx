"use client";

import Link from "next/link";
import { ArrowRight, BookOpen, Clock, Link2, Search } from "lucide-react";
import { LanguageSwitch, useLocale } from "@/components/ui/Language";

export default function About() {
  const vi = useLocale() === "vi";
  const cards = [
    [Search, vi ? "Tìm mọi nguồn liên quan" : "Search across relevant sources", vi ? "Nhập một chủ đề hoặc câu hỏi. Hệ thống tìm tin tức, trang web và bài nghiên cứu liên quan — không giới hạn ở một vài website cố định." : "Enter a topic or question. The system searches related news, websites and research, rather than being limited to a few fixed sites."],
    [Link2, vi ? "Luôn có nguồn kiểm chứng" : "Always keep verifiable sources", vi ? "Mỗi kết quả hiển thị nguồn và đường dẫn gốc để bạn đọc toàn văn, đánh giá độ tin cậy và dùng làm dẫn chứng." : "Every result retains its source and original link for full reading, reliability checks and citation."],
    [BookOpen, vi ? "AI hỗ trợ đọc hiểu" : "AI supports comprehension", vi ? "AI đọc các trích đoạn và abstract có sẵn để tóm tắt ý chính, giúp bạn sàng lọc nhanh nguồn hữu ích." : "AI uses available excerpts and abstracts to summarize key points, helping you screen useful material faster."],
    [Clock, vi ? "Theo dõi theo thời gian" : "Follow changes over time", vi ? "Tin được lưu cùng thời gian xuất bản khi nguồn cung cấp. Chủ đề đang mở có thể được làm mới định kỳ để theo dõi diễn biến mới." : "News retains available publication dates. Open topics can refresh periodically to follow new developments."],
  ] as const;

  return <main className="min-h-screen bg-base text-ink">
    <div className="mx-auto max-w-5xl px-6 py-8">
      <nav className="mb-20 flex items-center justify-between gap-4">
        <Link href="/news" className="font-semibold">VesperSignal <span className="text-ink-muted">Research & News</span></Link>
        <LanguageSwitch />
      </nav>

      <span className="rounded-full border border-stroke px-3 py-1 text-xs text-ink-muted">{vi ? "Ý TƯỞNG DỰ ÁN · SẮP CÓ DEMO" : "PROJECT VISION · DEMO COMING SOON"}</span>
      <h1 className="mt-7 max-w-3xl text-4xl font-semibold leading-tight md:text-6xl">{vi ? "Ít tab hơn. Nhiều thời gian để hiểu hơn." : "Fewer tabs. More time to understand."}</h1>
      <p className="mt-7 max-w-3xl text-lg leading-relaxed text-ink-muted">{vi ? "Dự án bắt đầu từ một vấn đề quen thuộc với sinh viên và người làm nghiên cứu: mất quá nhiều thời gian để tìm kiếm, đọc và quản lý nguồn tài liệu. Báo cáo, khóa luận và nghiên cứu khoa học thường bị phân tán qua hàng loạt tab trình duyệt." : "The project began with a familiar problem for students and researchers: too much time spent finding, reading and managing sources across countless browser tabs."}</p>
      <div className="my-9 flex flex-wrap gap-4">
        <Link href="/news" className="inline-flex items-center gap-2 rounded-xl bg-brand px-5 py-3 text-base">{vi ? "Khám phá nguồn" : "Explore sources"}<ArrowRight size={17}/></Link>
        <Link href="/research-notes" className="rounded-xl border border-stroke px-5 py-3">{vi ? "Ghi chú nghiên cứu" : "Research notes"}</Link>
      </div>

      <div className="my-16 grid gap-6 md:grid-cols-2">
        {cards.map(([Icon, title, body]) => <section key={title} className="rounded-2xl border border-stroke p-7"><Icon size={24}/><h2 className="my-4 text-xl font-semibold">{title}</h2><p className="leading-relaxed text-ink-muted">{body}</p></section>)}
      </div>

      <section className="rounded-2xl border border-stroke p-8">
        <span className="text-xs text-ink-muted">{vi ? "VÍ DỤ TÌM KIẾM" : "SEARCH EXAMPLE"}</span>
        <h2 className="my-5 text-2xl">{vi ? "“AI đang được ứng dụng như thế nào trong giáo dục đại học?”" : "“How is AI being used in higher education?”"}</h2>
        <div className="grid gap-6 md:grid-cols-[1.2fr_.8fr]">
          <div><h3 className="mb-3 text-sm font-semibold">AI Summary</h3><p className="leading-relaxed text-ink-muted">{vi ? "Trí tuệ nhân tạo đang được ứng dụng trong giáo dục đại học để hỗ trợ học tập cá nhân hóa, trợ lý học tập AI, tự động hóa một phần hoạt động giảng dạy và phân tích quá trình học của sinh viên. Bên cạnh đó là các vấn đề về độ chính xác, đạo văn, quyền riêng tư và cách đánh giá năng lực người học." : "Artificial intelligence is being used in higher education for personalized learning, AI learning assistants, partial teaching automation, and analysis of student learning. It also raises issues of accuracy, plagiarism, privacy, and assessment."}</p></div>
          <div className="rounded-xl bg-surface-2 p-5"><h3 className="mb-3 text-sm font-semibold">Sources</h3><ol className="space-y-3 text-sm text-ink-muted"><li>[1] {vi ? "Bài nghiên cứu — Tác giả — Năm xuất bản" : "Research paper — Author — Year"}<br/><span className="text-brand">🔗 {vi ? "Link nguồn" : "Source link"}</span></li><li>[2] {vi ? "Tài liệu/tổ chức liên quan" : "Related organisation/document"}<br/><span className="text-brand">🔗 {vi ? "Link nguồn" : "Source link"}</span></li></ol></div>
        </div>
      </section>

      <section className="my-16 max-w-3xl"><h2 className="text-2xl font-semibold">{vi ? "AI không làm nghiên cứu thay bạn." : "AI does not do research for you."}</h2><p className="mt-5 leading-relaxed text-ink-muted">{vi ? "Mục tiêu của dự án là giảm thời gian tìm kiếm và sàng lọc thông tin, giúp bạn nhanh chóng nhận ra nguồn nào hữu ích cho báo cáo, khóa luận hoặc nghiên cứu. Việc đánh giá độ tin cậy, đọc toàn văn và đưa ra kết luận vẫn cần phán đoán của người nghiên cứu." : "The goal is to reduce the time spent searching and screening, so you can identify useful evidence for reports, dissertations or research. Reliability assessment, full reading and conclusions remain the researcher’s responsibility."}</p><p className="mt-5 text-sm leading-relaxed text-ink-muted">{vi ? "Dự án sẽ sớm có bản demo. Hiện hệ thống không cam kết đọc được toàn văn mọi website hoặc bao phủ toàn bộ Internet; AI chỉ nên được dùng để hỗ trợ đọc hiểu và luôn phải đối chiếu nguồn gốc." : "A demo is coming soon. The system does not promise full-text access to every website or complete Internet coverage; AI should only support comprehension and always be checked against original sources."}</p></section>
      <footer className="border-t border-stroke py-8 text-sm text-ink-muted">VesperSignal · {vi ? "Tìm nhanh. Hiểu rõ. Luôn có nguồn." : "Find faster. Understand better. Keep the evidence."}</footer>
    </div>
  </main>;
}
