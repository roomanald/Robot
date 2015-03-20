from PIL import Image, ImageChops, ImageOps
import cStringIO
import pygame
from pygame.locals import *

def convertPygameSurfaceToMemoryStream(surface, imageSize)
	imstring = pygame.image.tostring(surface,"RGB")
	im = Image.fromstring("RGB", imageSize, imstring)
	memf = cStringIO.StringIO()
	im.save(memf, "JPEG")
	return memf
