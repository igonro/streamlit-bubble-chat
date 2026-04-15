/* ─── Types ─── */

export interface Message {
  role: "user" | "assistant" | "system";
  name?: string;
  content: string;
}

export interface AssistantConfig {
  icon: string;
  avatar_bg: string;
  bubble_bg?: string;
  bubble_color?: string;
}

export interface BubbleChatData {
  messages: Message[];
  type: "simple" | "avatar";
  unread_count: number;
  play_sound_on_unread: boolean;
  window_title: string;
  theme_color: string | null;
  show_names: boolean;
  assistant_config: Record<string, AssistantConfig>;
  user_icon: string;
  user_icon_bg: string;
  name_colors: Record<string, string>;
  is_open: boolean;
  is_maximized: boolean;
}

export const FALLBACK_ASSISTANT: AssistantConfig = {
  icon: "🤖",
  avatar_bg: "",
};
