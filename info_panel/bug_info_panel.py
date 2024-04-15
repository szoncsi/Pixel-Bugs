import pygame

class BugInfoPanel:
    def __init__(self, screen, font, pos, size, bg_color=(0, 0, 0, 128)):
        self.screen = screen
        self.font = font
        self.pos = pos
        self.size = size
        self.bg_color = bg_color
        self.visible = False
        self.selected_bug = None
    
    def set_selected_bug(self, bug):
        self.selected_bug = bug
        self.visible = True if bug is not None else False
    
    def format_and_sort_genotype(self, color_genotype, pigment_genotype):
        sorted_color_genotype = ''.join(sorted(color_genotype, key=lambda x: (-x.isupper(), x)))
        sorted_pigment_genotype = ''.join(sorted(pigment_genotype, key=lambda x: (-x.isupper(), x)))

        combined_genotype = f"{sorted_color_genotype}{sorted_pigment_genotype}"

        return combined_genotype


    def draw(self):
        if not self.visible or self.selected_bug is None:
            return

        s = pygame.Surface(self.size, pygame.SRCALPHA)
        s.fill(self.bg_color)
        self.screen.blit(s, self.pos)

        attributes = [
            f"Gender: {self.selected_bug.gender}",
            f"Energy: {self.selected_bug.energy:.1f}",
            f"Has Mated: {self.selected_bug.hasMated}",
            f"Lifespan: {self.selected_bug.lifespan}",
            f"Movement Speed: {self.selected_bug.movement_speed:.1f}",
            f"Toughness: {self.selected_bug.toughness}",
            f"Sensing Distance: {self.selected_bug.sensing_distance}",
            f"Generation: {self.selected_bug.generation}",
            f"Color/Pigment Genotype: {self.format_and_sort_genotype(self.selected_bug.genotype['color'], self.selected_bug.genotype['pigment'])}",
        ]
        
        if self.selected_bug.gender == "female":
            attributes.append(f"Is Gravid: {self.selected_bug.isGravid}")

        for i, attribute in enumerate(attributes):
            text = self.font.render(attribute, True, (255, 255, 255))
            self.screen.blit(text, (self.pos[0] + 10, self.pos[1] + 10 + i * 20))