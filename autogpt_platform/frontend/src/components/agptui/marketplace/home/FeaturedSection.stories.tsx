import type { Meta, StoryObj } from "@storybook/react";
import { FeaturedSection } from "./FeaturedSection";

const meta = {
  title: "AGPTUI/Marketplace/Home/FeaturedSection",
  component: FeaturedSection,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    featuredAgents: { control: "object" },
    onCardClick: { action: "clicked" },
  },
} satisfies Meta<typeof FeaturedSection>;

export default meta;
type Story = StoryObj<typeof meta>;

const mockFeaturedAgents = [
  {
    agentName: "SEO Optimizer Pro",
    creatorName: "AI Solutions Inc.",
    description:
      "Boost your website's search engine rankings with our advanced AI-powered SEO optimization tool.",
    runs: 50000,
    rating: 4.7,
  },
  {
    agentName: "Content Writer AI",
    creatorName: "WordCraft AI",
    description:
      "Generate high-quality, engaging content for your blog, social media, or marketing campaigns.",
    runs: 75000,
    rating: 4.5,
  },
  {
    agentName: "Data Analyzer Lite",
    creatorName: "DataTech",
    description: "A basic tool for analyzing small to medium-sized datasets.",
    runs: 10000,
    rating: 3.8,
  },
];

export const Default: Story = {
  args: {
    featuredAgents: mockFeaturedAgents,
    onCardClick: (agentName: string) => console.log(`Clicked on ${agentName}`),
  },
};

export const SingleAgent: Story = {
  args: {
    featuredAgents: [mockFeaturedAgents[0]],
    onCardClick: (agentName: string) => console.log(`Clicked on ${agentName}`),
  },
};

export const NoAgents: Story = {
  args: {
    featuredAgents: [],
    onCardClick: (agentName: string) => console.log(`Clicked on ${agentName}`),
  },
};