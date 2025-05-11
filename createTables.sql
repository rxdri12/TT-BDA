-- Tabla Usuario
CREATE TABLE Usuario (
    idUsuario BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    pseudonimo VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    fechaNacimiento DATE NOT NULL
);

-- Tabla Artista
CREATE TABLE Artista (
    idArtista BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    nacionalidad VARCHAR(50) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    numeroSeguidores INTEGER NOT NULL CHECK(numeroSeguidores >= 0),
    ranking INTEGER NOT NULL CHECK(ranking > 0)
);

-- Tabla Cancion
CREATE TABLE Cancion (
    idCancion BIGSERIAL PRIMARY KEY,
    idArtista BIGINT NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    tiempoDuracion INTEGER NOT NULL CHECK (tiempoDuracion > 0),
    fechaPublicacion DATE NOT NULL,
    genero VARCHAR(100) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    FOREIGN KEY (idArtista) REFERENCES Artista(idArtista)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Tabla Guarda (Usuario guarda Cancion)
CREATE TABLE Guarda (
    idUsuario BIGINT NOT NULL,
    idCancion BIGINT NOT NULL,
    PRIMARY KEY (idUsuario, idCancion),
    FOREIGN KEY (idUsuario) REFERENCES Usuario(idUsuario)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (idCancion) REFERENCES Cancion(idCancion)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Tabla Sigue (Usuario sigue a Artista)
CREATE TABLE Sigue (
    idUsuario BIGINT NOT NULL,
    idArtista BIGINT NOT NULL,
    PRIMARY KEY (idUsuario, idArtista),
    FOREIGN KEY (idUsuario) REFERENCES Usuario(idUsuario)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (idArtista) REFERENCES Artista(idArtista)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);