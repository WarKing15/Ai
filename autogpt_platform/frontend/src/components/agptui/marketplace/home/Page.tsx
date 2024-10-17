import * as React from "react";
import { Navbar } from "../../Navbar";
import { HeroSection } from "./HeroSection";
import { FeaturedSection } from "./FeaturedSection";
import { AgentsSection } from "../../AgentsSection";
import { BecomeACreator } from "../../BecomeACreator";
import { FeaturedCreators } from "./FeaturedCreators";
import { Separator } from "../../../ui/separator";
import { IconType } from "../../../ui/icons";
interface PageProps {
  userName: string;
  userEmail: string;
  navLinks: { name: string; href: string }[];
  activeLink: string;
  featuredAgents: {
    agentName: string;
    agentImage: string;
    creatorName: string;
    description: string;
    runs: number;
    rating: number;
  }[];
  topAgents: {
    agentName: string;
    agentImage: string;
    avatarSrc: string;
    description: string;
    runs: number;
    rating: number;
  }[];
  featuredCreators: {
    creatorName: string;
    creatorImage: string;
    bio: string;
    agentsUploaded: number;
    avatarSrc: string;
  }[];
  menuItemGroups: {
    groupName?: string;
    items: {
      icon: IconType;
      text: string;
      href?: string;
      onClick?: () => void;
    }[];
  }[];
}

export const Page: React.FC<PageProps> = ({
  userName,
  userEmail,
  navLinks,
  activeLink,
  featuredAgents,
  topAgents,
  featuredCreators,
  menuItemGroups,
}) => {
  const handleSearch = (query: string) => {
    console.log("Search query:", query);
    // Implement search functionality
  };

  const handleFilterChange = (selectedFilters: string[]) => {
    console.log("Selected filters:", selectedFilters);
    // Implement filter functionality
  };

  const handleCardClick = (agentName: string) => {
    console.log("Clicked on agent:", agentName);
    // Implement card click functionality
  };

  const handleProfileClick = () => {
    console.log("Profile clicked");
    // Implement profile click functionality
  };

  const handleBecomeCreator = () => {
    console.log("Become a Creator clicked");
    // Implement become a creator functionality
  };

  return (
    <div className="mx-auto w-screen max-w-[1360px]">
      <Navbar
        userName={userName}
        userEmail={userEmail}
        links={navLinks}
        activeLink={activeLink}
        menuItemGroups={menuItemGroups}
      />
      <main className="px-4">
        <HeroSection
          onSearch={handleSearch}
          onFilterChange={handleFilterChange}
        />
        <FeaturedSection
          featuredAgents={featuredAgents}
          onCardClick={handleCardClick}
        />
        <Separator />
        <AgentsSection
          sectionTitle="Top Agents"
          agents={topAgents}
          onCardClick={handleCardClick}
        />
        <Separator />
        <FeaturedCreators
          featuredCreators={featuredCreators}
          onCardClick={handleCardClick}
        />
        <Separator />
        <BecomeACreator
          title="Want to contribute?"
          heading="We're always looking for more Creators!"
          description="Join our ever-growing community of hackers and tinkerers"
          buttonText="Become a Creator"
          onButtonClick={handleBecomeCreator}
        />
      </main>
    </div>
  );
};
