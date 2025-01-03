import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import random
import time

from geometic_objects import Point, Segment, Trapezoid, distance
from search_structure import SearchDAG


from dataclasses import dataclass


# input odcinków
points = []
segments = []
sought_point = Point(random.uniform(0, 1), random.uniform(0, 1))
seg_start = None


def generate_random_segments(N):
    global segments
    i = 0
    while i < N:
        s = Point(random.uniform(0, 1), random.uniform(0, 1))
        t = Point(random.uniform(0, 1), random.uniform(0, 1))
        new_segment = Segment(s, t)

        if not any(new_segment.intersects(existing_segment) for existing_segment in segments):
            segments.append(new_segment)
            i += 1


def input_segments():
    """
    Funkcja pozwala na interaktywne zadawanie odcinków. Przy kliknięciu zadawany jest pierwszy punkt odcinka,
    przy następnym kliknięciu zadawany drugi i oba punkty są łączone. Jeżeli kursor był wystarczająco blisko
    istniejącego już punktu, to punkty te są łączone, co pozwala na zadawanie odcinków o wspólnym punkcie. Przy ostatnim
    kliknięciu zadawany jest szukany punkt. Jeżeli ostatni punkt nie został zadany, to jest generowany losowo.
    Naciśnięcie zamknięcia okna (X) kończy zadawanie punktów. Odcinki nie powinny się przecinać.
    Odcinki są dodawane do listy segments.
    global sought_point, segments, points, seg_start
    :return: None
    """
    global sought_point, segments, points, seg_start

    def onclick(event):
        nonlocal ax
        global seg_start, sought_point
        precision = 0.01  # określa jak blisko trzeba kliknąć danego punktu, żeby uznać go za ten same punkt

        x, y = event.xdata, event.ydata
        curr = Point(x, y)
        if not seg_start:  # początek odcinka
            for p in points:
                if distance(p, curr) < precision:  # punkt curr już istnieje
                    seg_start = p
                    plt.draw()
                    return
            points.append(curr)
            ax.plot(x, y, 'ro', markersize=5)
            seg_start = curr
            sought_point = curr
        else:  # koniec odcinka
            for p in points:
                if distance(p, curr) < precision:  # punkt curr już istnieje
                    ax.plot([seg_start.x, p.x], [seg_start.y, p.y], 'r-')
                    if seg_start != p:
                        segments.append(Segment(seg_start, p))
                    seg_start = None
                    plt.draw()
                    return
            points.append(curr)
            ax.plot(x, y, 'ro', markersize=5)
            ax.plot([seg_start.x, x], [seg_start.y, y], 'r-')
            if seg_start != curr:
                segments.append(Segment(seg_start, curr))
            seg_start = None
        plt.draw()

    fig, ax = plt.subplots()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    cursor_default = Cursor(ax, useblit=True, color='blue', linewidth=1)
    fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()
    if not seg_start:
        sought_point = Point(random.uniform(0, 1), random.uniform(0, 1))



























def find_point(searchStructure, point):
    """
    :param searchStructure: SearchDAG
    :param point: Point
    :return: Trapezoid
    Funkcja zwraca trapezoid, w którym zawiera się poszukiwany punkt.
    """
    return searchStructure.search(point, None)


def measure_time(N, M, O):
    global segments
    """
    :param N:: int :: liczba map do wygenerowania
    :param M:: int :: liczba odcinków dla każdej mapy
    :param O:: int :: liczba punktów do znalezienia dla każdej z map
    :return: całkowity czas wykonania
    """
    execution_time = 0
    for i in range(N):
        segments = []
        generate_random_segments(M)

        start_time = time.time()
        structure = trapezoidal_map(segments)
        for j in range(O):
            point = Point(random.uniform(0, 1), random.uniform(0, 1))
            find_point(structure, point)
        end_time = time.time()
        execution_time += end_time - start_time

    return execution_time


# wizualizacja
plot_number = 1


def point_to_tuple(point):
    """
    :param point: Point
    :return: (x,y)
    """
    return point.x, point.y


def points_to_tuples(points):
    """
    :param points: Lista Punktów [Point]
    :return: Lista krotek [(x,y)]
    """
    tuples = []
    for p in points:
        tuples.append((p.x, p.y))
    return tuples


def add_trapezoid(vis, trapezoid, history):
    """
    :param vis: Visualizer()
    :param trapezoid: Trapezoid
    :param history: lista zawierający dodane figury przy jednym dodawaniu [[figures]]
    :return: None
    Funkcja służy do dodania dwóch pionowych odcinków do wizualizacji.
    """
    # y coordinates of intersections
    try:
        upperLeft = trapezoid.top_segment.a * trapezoid.left_point.x + trapezoid.top_segment.b
        upperRight = trapezoid.top_segment.a * trapezoid.right_point.x + trapezoid.top_segment.b
        lowerLeft = trapezoid.bottom_segment.a * trapezoid.left_point.x + trapezoid.bottom_segment.b
        lowerRight = trapezoid.bottom_segment.a * trapezoid.right_point.x + trapezoid.bottom_segment.b

        i = len(history)
        trapezoid.place_in_history = i
        history.append([])
        # history[i].append(vis.add_line_segment(((trapezoid.leftP.x, upperLeft), (trapezoid.rightP.x, upperRight)), color='gray'))
        history[i].append(
            vis.add_line_segment(((trapezoid.left_point.x, upperLeft), (trapezoid.left_point.x, lowerLeft)), color='red'))
        # history[i].append(vis.add_line_segment(((trapezoid.leftP.x, lowerLeft), (trapezoid.rightP.x, lowerRight)), color='gray'))
        history[i].append(
            vis.add_line_segment(((trapezoid.right_point.x, upperRight), (trapezoid.right_point.x, lowerRight)), color='red'))
    except Exception as e:
        print(f"Trapez {trapezoid} nie został prawidłowo skonstruowany")
        sys.exit(-1)


def remove_trapezoid(vis, i, history):
    """
    :param vis: Visualizer()
    :param i:: int :: numer indeksu w tabeli history do usunięcia
    :param history: lista zawierający dodane figury przy jednym dodawaniu [[figures]]
    :return: None
    """
    if i and history[i]:
        for j in history[i]:
            vis.remove_figure(j)


def add_trapezoid_blue(vis, trapezoid):
    """
    :param vis: Visualizer()
    :param trapezoid: Trapezoid
    :return: Lista dodanych figur
    Funkcja koloruje wybrany trapez na niebiesko. Używane do zaznaczenia szukanego trapezu.
    """
    # y coordinates of intersections
    upperLeft = trapezoid.top_segment.a * trapezoid.left_point.x + trapezoid.top_segment.b
    upperRight = trapezoid.top_segment.a * trapezoid.right_point.x + trapezoid.top_segment.b
    lowerLeft = trapezoid.bottom_segment.a * trapezoid.left_point.x + trapezoid.bottom_segment.b
    lowerRight = trapezoid.bottom_segment.a * trapezoid.right_point.x + trapezoid.bottom_segment.b

    figures = []
    figures.append(
        vis.add_line_segment(((trapezoid.left_point.x, upperLeft), (trapezoid.right_point.x, upperRight)), color='blue'))
    figures.append(vis.add_line_segment(((trapezoid.left_point.x, upperLeft), (trapezoid.left_point.x, lowerLeft)), color='blue'))
    figures.append(
        vis.add_line_segment(((trapezoid.left_point.x, lowerLeft), (trapezoid.right_point.x, lowerRight)), color='blue'))
    figures.append(
        vis.add_line_segment(((trapezoid.right_point.x, upperRight), (trapezoid.right_point.x, lowerRight)), color='blue'))
    return figures


def remove_figures(vis, figures):
    """
    :param vis: Visualizer()
    :param figures: Lista figur
    :return: None
    """
    for figure in figures:
        vis.remove_figure(figure)


def add_border(vis, border):
    """
    :param vis: Visualizer()
    :param border: Trapezoid
    :return: None
    Funkcja rysuje prostokąt ograniczający.
    """
    upperLeft = point_to_tuple(border.top_segment.start)
    upperRight = point_to_tuple(border.top_segment.end)
    lowerLeft = point_to_tuple(border.bottom_segment.start)
    lowerRight = point_to_tuple(border.bottom_segment.end)

    vis.add_line_segment((upperLeft, upperRight), color='red')
    vis.add_line_segment((upperLeft, lowerLeft), color='red')
    vis.add_line_segment((lowerLeft, lowerRight), color='red')
    vis.add_line_segment((upperRight, lowerRight), color='red')


def add_segment(vis, segment, colour):
    """
    :param vis: Visualizer()
    :param segment: Segment
    :param colour: String
    :return: None
    Rysuje podany odcinek na wybrany kolor.
    """
    start = segment.start
    end = segment.end
    vis.add_line_segment((point_to_tuple(start), point_to_tuple(end)), color=colour)


def save(vis, save_per_step=False):
    """
    :param vis: Visualizer()
    :param save_per_step:: True/False :: określa czy wizualizacja ma zapisywać obraz po każdym dodanym odcinku
    :return: None
    Zapisuje obraz do folderu, w którym znajduje się ten plik.
    """
    if (save_per_step):
        global plot_number
        vis.save('plot%d' % plot_number)
        plot_number += 1


def trapezoidal_map_visuals(segments, save_per_step=False):
    """
    global sought_point
    :param segments: Lista nieprzecinających się Segmentów [Segment]
    :param save_per_step:: True/False :: określa czy wizualizacja ma zapisywać obraz po każdym dodanym odcinku
    :return: SearchDAG
    Funkcja tworzy mapę trapezoidalny, wizualizuje ją, buduje strukturę poszukiwań
    i zaznacza prostokąt z szukanym punktem na niebiesko.
    Przy save_per_step ustawionym na False zapisywane są dwa obrazy: początkowy układ odcinków oraz
    obraz zbudowanej mapy trapezów.
    """
    # zapisuje obraz wprowadzonych odcinków i punktu
    inputed = Visualizer()
    for segment in segments:
        add_segment(inputed, segment, 'red')
    inputed.add_point(point_to_tuple(sought_point))
    save(inputed, True)

    random.shuffle(segments)

    # znajduje prostokąt ograniczający, ustawia go jako root SearchDAG
    rootTrapezoid = FindBorder(segments)
    rootNode = Leafnode(trapezoid=rootTrapezoid, type='leaf')
    searchStructure = SearchDAG(rootNode)

    vis = Visualizer()

    vis.add_point(point_to_tuple(sought_point))
    add_border(vis, rootTrapezoid)

    save(vis, save_per_step)

    history = [[]]
    for segment in segments:
        add_segment(vis, segment, 'black')
        save(vis, save_per_step)

        # znajduje trapez, w którym znajduje się początek odcinku oraz trapez, w którym znajduje się jego koniec
        startTrapezoid = searchStructure.search(segment.near_start(), searchStructure.root)
        endTrapezoid = searchStructure.search(segment.near_end(), searchStructure.root)

        intersectingTrapezoids = find_intersected_trapezoids(segment, startTrapezoid)

        for trapezoid in intersectingTrapezoids:
            remove_trapezoid(vis, trapezoid.place_in_history, history)

        if startTrapezoid == endTrapezoid:
            addedTrapezoids = insertSegmentInOneTrapezoid(searchStructure, intersectingTrapezoids[0],
                                                          segment)  # tylko jeden trapez w intersectingTrapezoids
        else:
            addedTrapezoids = insertSegmentInManyTrapezoids(searchStructure, intersectingTrapezoids, segment)

        for t in addedTrapezoids:
            add_trapezoid(vis, t, history)

        save(vis, save_per_step)
        add_segment(vis, segment, 'gray')

    # zaznacza na niebiesko trapez z szukanym punktem, zapisuje obraz
    soughtTrapezoid = searchStructure.search(sought_point, searchStructure.root)
    add_trapezoid_blue(vis, soughtTrapezoid)
    save(vis, True)

    return searchStructure


def add_trapezoid_blue_plt(ax, trapezoid):
    """
    :param ax: Axes
    :param trapezoid: Trapezoid
    :return: Lista dodanych figur
    Funkcja koloruje wybrany trapez na niebiesko. Używane do zaznaczenia szukanego trapezu.
    Ta wersja funkcji używa bezpośrednio biblioteki matplotlib.
    """
    # y coordinates of intersections
    upperLeft = trapezoid.top_segment.a * trapezoid.left_point.x + trapezoid.top_segment.b
    upperRight = trapezoid.top_segment.a * trapezoid.right_point.x + trapezoid.top_segment.b
    lowerLeft = trapezoid.bottom_segment.a * trapezoid.left_point.x + trapezoid.bottom_segment.b
    lowerRight = trapezoid.bottom_segment.a * trapezoid.right_point.x + trapezoid.bottom_segment.b

    line1, = ax.plot((trapezoid.left_point.x, trapezoid.right_point.x), (upperLeft, upperRight), color="blue")
    line2, = ax.plot((trapezoid.left_point.x, trapezoid.left_point.x), (upperLeft, lowerLeft), color="blue")
    line3, = ax.plot((trapezoid.left_point.x, trapezoid.right_point.x), (lowerLeft, lowerRight), color="blue")
    line4, = ax.plot((trapezoid.right_point.x, trapezoid.right_point.x), (upperRight, lowerRight), color="blue")
    return line1, line2, line3, line4


def trapezoidal_map_interactive(segments):
    """
    :param segments: Lista nieprzecinających się Segmentów [Segment]
    :return: None
    Funkcja tworzy mapę trapezoidalny, wizualizuje ją, buduje strukturę poszukiwań
    Wyświetla zbudowaną mapę, przy kliknięciu pozwala wprowadzić punkt, kolorując trapez,
     w którym znajduje się wprowadzony punkt na niebiesko.
    """
    random.shuffle(segments)

    # znajduje prostokąt ograniczający, ustawia go jako root SearchDAG
    rootTrapezoid = FindBorder(segments)
    rootNode = Leafnode(trapezoid=rootTrapezoid, type='leaf')
    searchStructure = SearchDAG(rootNode)

    vis = Visualizer()

    add_border(vis, rootTrapezoid)

    history = [[]]
    for segment in segments:
        add_segment(vis, segment, 'black')

        # znajduje trapez, w którym znajduje się początek odcinku oraz trapez, w którym znajduje się jego koniec
        startTrapezoid = searchStructure.search(segment.near_start(), searchStructure.root)
        endTrapezoid = searchStructure.search(segment.near_end(), searchStructure.root)

        intersectingTrapezoids = find_intersected_trapezoids(segment, startTrapezoid)

        for trapezoid in intersectingTrapezoids:
            remove_trapezoid(vis, trapezoid.place_in_history, history)

        if startTrapezoid == endTrapezoid:
            addedTrapezoids = insertSegmentInOneTrapezoid(searchStructure, intersectingTrapezoids[0],
                                                          segment)  # tylko jeden trapez w intersectingTrapezoids
        else:
            addedTrapezoids = insertSegmentInManyTrapezoids(searchStructure, intersectingTrapezoids, segment)

        for t in addedTrapezoids:
            add_trapezoid(vis, t, history)

        add_segment(vis, segment, 'gray')

    # rysuje mapę i pozwala na interakcje z nią
    inputed_point = None
    current = None
    line1 = None
    line2 = None
    line3 = None
    line4 = None

    def onclick(event):
        nonlocal inputed_point, current, vis, fig, ax, line1, line2, line3, line4
        if inputed_point:
            current.remove()
            line1.remove()
            line2.remove()
            line3.remove()
            line4.remove()

        x, y = event.xdata, event.ydata
        inputed_point = Point(x, y)
        current, = ax.plot(x, y, 'bo', markersize=5, label="current")

        trapezoid = searchStructure.search(inputed_point, None)
        line1, line2, line3, line4 = add_trapezoid_blue_plt(ax, trapezoid)

        plt.draw()

    def vis_draw():
        nonlocal vis, ax
        for figure in vis.data:
            if not figure.to_be_removed:
                figure.draw(ax)

    fig, ax = plt.subplots()
    vis_draw()
    ax.autoscale()
    cursor_default = Cursor(ax, useblit=True, color='blue', linewidth=1)
    fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()


# wprowadzanie ręczne lub generowanie odcinków
input_segments()
# generate_random_segments(5)

# opcje wizualizacji i interaktywna
# trapezoidal_map_visuals(segments=segments, save_per_step=False)
trapezoidal_map_interactive(segments)
