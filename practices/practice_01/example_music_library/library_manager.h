#pragma once

#include <core/library.h>

#include <string>
#include <optional>
#include <cstddef>

namespace mlm {

class LibraryManager {
public:
    LibraryManager(mlm::Library& lib) 
        : lib_reference_(lib) {}

    /* Add track */
    void addTrack(const std::string& name /* other args */);

    /* Update track by name */
    bool updateTrack(const std::string& name /* args */);

    /* Delete track by name */
    bool deleteTrack(const std::string& name);

    /* Get track reference by name */
    std::shared_ptr<mlm::Track> getTrack(const std::string& name);

    /* Return track count */
    std::size_t trackCount() const;
    
private:
    std::optional<std::size_t> getTrackIndex(const std::string& name) const;

    mlm::Library& lib_reference_;
};

} // namespace mlm